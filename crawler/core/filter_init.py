import json
import re
from pathlib import Path
from urllib.request import urlopen


FILTER_INIT_PATTERN = re.compile(r"Filter\.init\(\s*([\s\S]*?)\s*\);")
DEFAULT_FILTER_PAGE_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "filter_pages"


def extract_filter_init_payload(html_text):
    """从 HTML 文本中提取 Filter.init 的原始 JSON 载荷。"""
    match = FILTER_INIT_PATTERN.search(html_text)
    if match is None:
        raise ValueError("未找到 Filter.init 数据")

    return json.loads(match.group(1))


def build_filter_page_output_path(page_name):
    """为抓取到的页面 HTML 构建默认输出路径。"""
    return DEFAULT_FILTER_PAGE_OUTPUT_DIR / f"{page_name}.html"


def build_filter_json_output_path(html_path):
    """为本地 HTML 构建默认的 filters JSON 输出路径。"""
    html_file = Path(html_path)
    return html_file.with_suffix(".filters.json")


def write_filter_page_html(url, output_path=None, fetch_url=None):
    """抓取指定 URL 并将 HTML 落地到本地文件。"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fetch_url = fetch_url or _fetch_url
    output_file.write_text(fetch_url(url), encoding="utf-8")
    return output_file


def write_filter_init_json(html_path, output_path=None):
    """从本地 HTML 中提取 Filter.init 并写出原始 JSON。"""
    html_file = Path(html_path)
    output_file = Path(output_path) if output_path is not None else build_filter_json_output_path(html_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    payload = extract_filter_init_payload(html_file.read_text(encoding="utf-8"))
    output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_file


def _fetch_url(url):
    """抓取页面 HTML 文本。"""
    with urlopen(url) as response:
        return response.read().decode("utf-8")
