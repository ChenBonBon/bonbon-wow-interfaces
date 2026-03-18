import json
import random
import re
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

from core.aggregator import ITEMS_BY_TASK_FILE_NAME, read_items_by_task
from core.run_report import write_run_report


LISTVIEW_ITEMS_PATTERN = re.compile(r"var\s+listviewitems\s*=\s*(\[[\s\S]*?\]);")
ZERO_RESULTS_MARKER = "Your criteria did not match any items."
UNQUOTED_OBJECT_KEY_PATTERN = re.compile(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)')
FETCH_CONCURRENCY = 3
FETCH_DELAY_MIN_SECONDS = 1.5
FETCH_DELAY_MAX_SECONDS = 3.0
CONSECUTIVE_FAILURE_LIMIT = 10


def extract_listviewitems_json(html_text):
    """从页面 HTML 中提取 listviewitems 数组文本。"""
    match = LISTVIEW_ITEMS_PATTERN.search(html_text)
    if match is None:
        raise ValueError("未找到 listviewitems 数据")
    return match.group(1)


def parse_items_from_html(html_text):
    """从页面 HTML 中解析最小 item 字段。"""
    if _is_zero_result_page(html_text):
        return []
    raw_items = json.loads(_normalize_listviewitems_json(extract_listviewitems_json(html_text)))
    return [
        {
            "itemId": item["id"],
            "name": item["name"],
        }
        for item in raw_items
    ]


def fetch_manifest_results(
    manifest_path,
    fetch_url=None,
    sleep_before_fetch=None,
    logger=None,
    timestamp_fn=None,
):
    """根据 manifest 抓取任务结果并回写状态。"""
    _process_manifest_results(
        manifest_path,
        allowed_statuses={"planned"},
        fetch_url=fetch_url,
        sleep_before_fetch=sleep_before_fetch,
        logger=logger,
        timestamp_fn=timestamp_fn,
    )


def retry_failed_manifest_results(
    manifest_path,
    fetch_url=None,
    sleep_before_fetch=None,
    logger=None,
    timestamp_fn=None,
):
    """重跑 manifest 中失败的任务并回写状态。"""
    _process_manifest_results(
        manifest_path,
        allowed_statuses={"failed"},
        fetch_url=fetch_url,
        sleep_before_fetch=sleep_before_fetch,
        logger=logger,
        timestamp_fn=timestamp_fn,
    )


def _process_manifest_results(
    manifest_path,
    allowed_statuses,
    fetch_url=None,
    sleep_before_fetch=None,
    logger=None,
    timestamp_fn=None,
):
    """根据允许状态集合处理 manifest 中的任务。"""
    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    fetch_url = fetch_url or _fetch_url
    sleep_before_fetch = sleep_before_fetch or _sleep_before_fetch
    logger = logger or print
    timestamp_fn = timestamp_fn or _default_timestamp
    output_dir = manifest_file.parent
    items_by_task = read_items_by_task(manifest_file)
    eligible_tasks = [task for task in manifest["tasks"] if task.get("status") in allowed_statuses]
    completed_count = 0
    fetched_count = 0
    failed_count = 0
    total_count = len(eligible_tasks)
    consecutive_failure_count = 0
    abort_metadata = None
    pending_tasks = iter(eligible_tasks)
    future_to_task = {}

    with ThreadPoolExecutor(max_workers=FETCH_CONCURRENCY) as executor:
        for _ in range(min(FETCH_CONCURRENCY, total_count)):
            _submit_next_task(
                executor,
                future_to_task,
                pending_tasks,
                output_dir,
                fetch_url,
                sleep_before_fetch,
                logger,
                timestamp_fn,
            )

        while future_to_task:
            done_futures, _pending = wait(
                future_to_task.keys(),
                return_when=FIRST_COMPLETED,
            )

            for future in done_futures:
                task = future_to_task.pop(future)
                try:
                    task_result = future.result()
                    items_by_task[task["task_id"]] = task_result
                    item_count = len(task_result.get("items", []))
                    task["status"] = "fetched"
                    task.pop("error_message", None)
                    fetched_count += 1
                    consecutive_failure_count = 0
                    _log(
                        logger,
                        timestamp_fn,
                        f"DONE {task['task_id']} item_count={item_count}",
                    )
                except Exception as error:
                    task["status"] = "failed"
                    items_by_task.pop(task["task_id"], None)
                    task["error_message"] = str(error)
                    failed_count += 1
                    consecutive_failure_count += 1
                    _log(logger, timestamp_fn, f"FAIL {task['task_id']}")

                    if abort_metadata is None and consecutive_failure_count >= CONSECUTIVE_FAILURE_LIMIT:
                        abort_metadata = {
                            "aborted_due_to_consecutive_failures": True,
                            "consecutive_failure_limit": CONSECUTIVE_FAILURE_LIMIT,
                        }
                        _log(
                            logger,
                            timestamp_fn,
                            (
                                "ABORT "
                                f"consecutive_failures={consecutive_failure_count} "
                                f"limit={CONSECUTIVE_FAILURE_LIMIT}"
                            ),
                        )

                _write_items_by_task(output_dir, items_by_task)
                _write_manifest(manifest_file, manifest)
                completed_count += 1
                if completed_count % 10 == 0:
                    _log(
                        logger,
                        timestamp_fn,
                        (
                            f"PROGRESS done={completed_count}/{total_count} "
                            f"fetched={fetched_count} failed={failed_count}"
                        ),
                    )

                if abort_metadata is None:
                    _submit_next_task(
                        executor,
                        future_to_task,
                        pending_tasks,
                        output_dir,
                        fetch_url,
                        sleep_before_fetch,
                        logger,
                        timestamp_fn,
                    )
    if abort_metadata is not None:
        write_run_report(manifest_file, extra_fields=abort_metadata)
        raise RuntimeError(
            f"连续失败达到上限 {CONSECUTIVE_FAILURE_LIMIT}，已中止抓取并写出任务总结。"
        )


def _submit_next_task(
    executor,
    future_to_task,
    pending_tasks,
    output_dir,
    fetch_url,
    sleep_before_fetch,
    logger,
    timestamp_fn,
):
    """向线程池补充一个待抓取任务。"""
    try:
        task = next(pending_tasks)
    except StopIteration:
        return False

    future = executor.submit(
        _fetch_task_result,
        task,
        output_dir,
        fetch_url,
        sleep_before_fetch,
        logger,
        timestamp_fn,
    )
    future_to_task[future] = task
    return True


def _write_manifest(manifest_file, manifest):
    """回写当前 manifest 状态。"""
    manifest_file.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _fetch_url(url):
    """抓取页面 HTML 文本。"""
    with urlopen(url) as response:
        return response.read().decode("utf-8")


def _fetch_task_result(task, output_dir, fetch_url, sleep_before_fetch, logger, timestamp_fn):
    """抓取单个任务并写入结果文件。"""
    _log(logger, timestamp_fn, f"START {task['task_id']}")
    sleep_before_fetch()
    html_text = fetch_url(task["url"])
    items = parse_items_from_html(html_text)
    return {
        "task_id": task["task_id"],
        "url": task["url"],
        "items": items,
    }


def _sleep_before_fetch(rand_uniform=None, sleep=None):
    """在请求前增加随机短暂停顿，降低持续高频请求特征。"""
    rand_uniform = rand_uniform or random.uniform
    sleep = sleep or time.sleep
    delay_seconds = rand_uniform(FETCH_DELAY_MIN_SECONDS, FETCH_DELAY_MAX_SECONDS)
    sleep(delay_seconds)


def _is_zero_result_page(html_text):
    """判断页面是否为 Wowhead 的零结果空列表页。"""
    return ZERO_RESULTS_MARKER in html_text


def _normalize_listviewitems_json(raw_text):
    """将 Wowhead 的 JS 对象字面量最小化转换为可被 json.loads 解析的文本。"""
    return UNQUOTED_OBJECT_KEY_PATTERN.sub(r'\1"\2"\3', raw_text)


def _default_timestamp():
    """返回日志使用的本地时间字符串。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log(logger, timestamp_fn, message):
    """统一输出带时间戳的抓取日志。"""
    logger(f"[{timestamp_fn()}] {message}")


def _write_items_by_task(output_dir, items_by_task):
    """回写单次运行的按任务结果总文件。"""
    results_path = Path(output_dir) / ITEMS_BY_TASK_FILE_NAME
    if not items_by_task:
        results_path.unlink(missing_ok=True)
        return
    results_path.write_text(
        json.dumps(items_by_task, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
