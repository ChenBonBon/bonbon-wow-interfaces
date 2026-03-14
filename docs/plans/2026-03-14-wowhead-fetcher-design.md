# Wowhead Fetcher 设计

**目标：** 为 crawler 增加一个 fetcher，读取 runner 产出的 `manifest.json`，抓取 Wowhead 页面，并把每个任务的结果保存为 JSON 文件。

## 输入与输出

输入：

- `crawler/outputs/<run_id>/manifest.json`

输出：

- `crawler/outputs/<run_id>/<task_id>.json`
- 更新后的 `crawler/outputs/<run_id>/manifest.json`

## 范围

第一版只实现：

- 读取 manifest
- 对每个 `status: planned` 任务请求页面
- 从 HTML 中提取 `var listviewitems = [...]`
- 为每条 item 提取：
  - `itemId`
  - `name`
- 把结果写成每任务一个 JSON 文件
- 成功后把任务状态更新为 `fetched`
- 失败后把任务状态更新为 `failed`

明确不做：

- 重试
- 限速
- 并发抓取
- 解析更多字段
- 增量续跑策略优化

## 数据来源策略

第一版不解析表格 DOM，也不追额外接口。

采用页面内嵌数据：

```javascript
var listviewitems = [...]
new Listview({ ..., data: listviewitems })
```

优点：

- 不依赖浏览器执行 JS
- 比 DOM 解析更稳定
- 页面已包含完整列表数据

## 模块设计

新增模块：

```text
crawler/core/fetcher.py
```

建议拆为以下接口：

1. `extract_listviewitems_json(html_text)`
- 从 HTML 中截出 `listviewitems` 的原始数组文本

2. `parse_items_from_html(html_text)`
- 把 `listviewitems` 解析成：

```json
[
  {
    "itemId": 2620,
    "name": "Augural Shroud"
  }
]
```

3. `fetch_manifest_results(manifest_path)`
- 读取 manifest
- 遍历 `planned` 任务
- 请求页面
- 写出 `<task_id>.json`
- 更新 manifest 状态

## 输出文件结构

每个任务输出一个 JSON 文件：

```json
{
  "task_id": "uncommon-head-cloth",
  "url": "https://www.wowhead.com/...",
  "items": [
    {
      "itemId": 2620,
      "name": "Augural Shroud"
    }
  ]
}
```

当前 item 级别只保留：

- `itemId`
- `name`

## 状态流转

manifest 中的任务状态第一版只使用：

- `planned`
- `fetched`
- `failed`

## 测试策略

优先测试：

- 能从样例 HTML 提取 `listviewitems`
- 能解析出 `itemId` 和 `name`
- 能从 manifest 驱动单任务抓取
- 抓取成功会写结果文件并更新状态为 `fetched`
- 抓取失败会更新状态为 `failed`

测试中使用本地样例 HTML 和可注入的 fetch 函数，避免单元测试依赖真实网络。
