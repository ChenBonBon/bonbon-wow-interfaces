# Wowhead Crawler

这个目录下的脚本用于：

- 生成 Wowhead 抓取任务
- 抓取结果并汇总
- 导出 Lua 数据给 `QuickDisenchant`
- 抓取 `Filter.init` 并生成 `normalized_mappings`
- 根据 `normalized_mappings` 生成 `crawler/core/mappings_data.py`

## 环境要求

- Python 3
- 在 `crawler/` 目录下执行命令

```bash
cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler
```

## 推荐入口

### 1. 运行完整抓取流程

默认读取：

- [tasks/wowhead_items.json](/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tasks/wowhead_items.json)

命令：

```bash
./bin/run_all.sh
```

也可以手动指定任务文件：

```bash
./bin/run_all.sh tasks/wowhead_items.example.json
```

这条命令会顺序执行：

1. 生成 `manifest.json`
2. 抓取 Wowhead 页面
3. 聚合为 `items.unique.json`
4. 导出 Lua 到：
   - [DisenchantableByWowhead.lua](/Users/bonbon/Documents/Code/bonbon-wow-interfaces/QuickDisenchant/DisenchantableByWowhead.lua)

### 2. 重跑失败任务

命令：

```bash
./bin/retry_failed.sh outputs/<run_id>/manifest.json
```

这条命令会顺序执行：

1. 只重跑 `failed` 状态的抓取任务
2. 对整个 run 重新聚合
3. 重新导出 Lua

如果 `manifest.json` 里还有未完成任务，导出会直接失败，不会写入残缺 Lua。

### 3. 抓取 Filter.init

命令：

```bash
./bin/fetch_filter_init.sh "https://www.wowhead.com/items/armor" armor
./bin/fetch_filter_init.sh "https://www.wowhead.com/items/weapons" weapons
```

第二个参数是输出名，可选。  
例如上面的命令会生成：

- `outputs/filter_pages/armor.html`
- `outputs/filter_pages/armor.filters.json`
- `outputs/filter_pages/weapons.html`
- `outputs/filter_pages/weapons.filters.json`

如果不传输出名，默认使用：

- `filter-page.html`
- `filter-page.filters.json`

### 4. 生成 mappings

命令：

```bash
./bin/generate_mappings.sh
```

默认读取：

- `outputs/filter_pages/normalized_mappings.json`

默认写入：

- [core/mappings_data.py](/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings_data.py)

也可以手动指定输入和输出：

```bash
./bin/generate_mappings.sh outputs/filter_pages/normalized_mappings.json core/mappings_data.py
```

### 5. 一键更新 mappings

命令：

```bash
./bin/update_mappings.sh
```

这条命令会顺序执行：

1. 并行抓取：
   - `armor`
   - `weapons`
2. 生成 `normalized_mappings.json`
3. 生成 [core/mappings_data.py](/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings_data.py)

如果 `armor` 或 `weapons` 任意一个抓取失败，脚本会直接退出，不会继续后续步骤。

## Python 脚本入口

如果你不想走 `bin/` 下的 shell wrapper，也可以直接运行 Python 模块。

### 任务与抓取流程

生成 manifest：

```bash
python3 -m scripts.generate_run tasks/wowhead_items.json
```

抓取任务：

```bash
python3 -m scripts.fetch_run outputs/<run_id>/manifest.json
```

汇总唯一物品：

```bash
python3 -m scripts.aggregate_run outputs/<run_id>/manifest.json
```

导出 Lua：

```bash
python3 -m scripts.export_lua outputs/<run_id>/manifest.json
```

总入口：

```bash
python3 -m scripts.run_all tasks/wowhead_items.json
```

失败任务重跑：

```bash
python3 -m scripts.retry_failed_run outputs/<run_id>/manifest.json
```

### Filter.init 与 mappings 流程

抓 HTML：

```bash
python3 -m scripts.fetch_filter_page "https://www.wowhead.com/items/armor" outputs/filter_pages/armor.html
```

提取 `Filter.init`：

```bash
python3 -m scripts.extract_filter_init outputs/filter_pages/armor.html
```

生成 `normalized_mappings.json`：

```bash
python3 -m scripts.generate_normalized_mappings
```

默认读取：

- `outputs/filter_pages/armor.html`
- `outputs/filter_pages/armor.filters.json`
- `outputs/filter_pages/weapons.html`
- `outputs/filter_pages/weapons.filters.json`

默认写入：

- `outputs/filter_pages/normalized_mappings.json`

生成 `mappings_data.py`：

```bash
python3 -m scripts.generate_mappings
```

说明：

- [core/mappings_data.py](/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings_data.py) 是自动生成的数据层
- [core/mappings.py](/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings.py) 是手写逻辑层，只负责校验和辅助函数

## 任务文件格式

任务文件位于：

- [tasks/wowhead_items.json](/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tasks/wowhead_items.json)
- [tasks/wowhead_items.example.json](/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tasks/wowhead_items.example.json)

当前 key 规则以 Wowhead label/value 为准，统一使用 `label_value` 形式。  
例如：

- `quality`: `uncommon_2`
- `slot`: `main_hand_21`
- `type`: `daggers_15`
- `query_filter`: `can_be_worn_equipped_195`

一个任务的示例：

```json
{
  "task_id": "rare-main-hand-dagger",
  "enabled": true,
  "quality": "rare_3",
  "category": "weapon",
  "slot": "main_hand_21",
  "type": "daggers_15",
  "query_filters": {
    "available_to_players_161": "yes",
    "can_be_worn_equipped_195": "yes",
    "disenchantable_8": "no"
  }
}
```

## 输出目录

抓取产物默认写到：

- [outputs](/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/outputs)

这些文件属于本地缓存与运行结果，已经被 `.gitignore` 忽略，不应提交到 git。

## 常用顺序

### 日常抓取并更新插件数据

```bash
./bin/run_all.sh
```

如果失败：

```bash
./bin/retry_failed.sh outputs/<run_id>/manifest.json
```

### 更新 mappings

```bash
./bin/fetch_filter_init.sh "https://www.wowhead.com/items/armor" armor
./bin/fetch_filter_init.sh "https://www.wowhead.com/items/weapons" weapons
python3 -m scripts.generate_normalized_mappings
./bin/generate_mappings.sh
```

或者直接：

```bash
./bin/update_mappings.sh
```
