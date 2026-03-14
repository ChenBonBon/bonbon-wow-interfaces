import json
import re
from pathlib import Path
from urllib.request import urlopen


LISTVIEW_ITEMS_PATTERN = re.compile(r"var\s+listviewitems\s*=\s*(\[[\s\S]*?\]);")


def extract_listviewitems_json(html_text):
    """从页面 HTML 中提取 listviewitems 数组文本。"""
    match = LISTVIEW_ITEMS_PATTERN.search(html_text)
    if match is None:
        raise ValueError("未找到 listviewitems 数据")
    return match.group(1)


def parse_items_from_html(html_text):
    """从页面 HTML 中解析最小 item 字段。"""
    raw_items = json.loads(extract_listviewitems_json(html_text))
    return [
        {
            "itemId": item["id"],
            "name": item["name"],
        }
        for item in raw_items
    ]


def fetch_manifest_results(manifest_path, fetch_url=None):
    """根据 manifest 抓取任务结果并回写状态。"""
    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    fetch_url = fetch_url or _fetch_url
    output_dir = manifest_file.parent

    for task in manifest["tasks"]:
        if task.get("status") != "planned":
            continue

        try:
            html_text = fetch_url(task["url"])
            items = parse_items_from_html(html_text)
            result_path = output_dir / f"{task['task_id']}.json"
            result_path.write_text(
                json.dumps(
                    {
                        "task_id": task["task_id"],
                        "url": task["url"],
                        "items": items,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            task["status"] = "fetched"
        except Exception:
            task["status"] = "failed"

    manifest_file.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _fetch_url(url):
    """抓取页面 HTML 文本。"""
    with urlopen(url) as response:
        return response.read().decode("utf-8")
