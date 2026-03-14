# Wowhead Lua Export 设计

**目标：** 仅在单次抓取运行全部成功时，将结果导出为 QuickDisenchant 可直接加载的 Lua 数据文件。

## 设计原则

- 不改动现有 JSON 数据源
- 独立生成新的 Lua 文件
- 输出结构以插件运行效率为优先
- 文件内容稳定排序，避免无意义 diff

## 输入与输出

输入：

- `crawler/outputs/<run_id>/manifest.json`

前置条件：

- `manifest.json` 中所有任务状态都必须为 `fetched`
- 同目录必须存在 `items.unique.json`
- 只要还有 `planned` 或 `failed`，就禁止导出

输出：

- `QuickDisenchant/DisenchantableByWowhead.lua`

## Lua 结构

输出内容固定为：

```lua
QD = QD or _G.QuickDisenchantNS
QD.WOWHEAD_DISENCHANTABLE_ITEM_IDS = {
  [1001] = true,
  [1002] = true,
}
```

说明：

- 只导出 `itemId`
- 不把 `name` 写入运行时表
- 所有 `itemId` 按升序输出

## 插件接入

需要把导出的 Lua 文件加入：

```text
QuickDisenchant/QuickDisenchant.toc
```

推荐加载顺序：

1. `Core.lua`
2. `DisenchantableByWowhead.lua`
3. `Data.lua`
4. 其他模块

这样数据表会在背包扫描逻辑之前就可用。

## 模块设计

新增：

```text
crawler/core/lua_exporter.py
crawler/scripts/export_lua.py
```

建议接口：

1. `render_lua_item_id_table(items)`
- 把唯一物品列表渲染成 Lua 文本

2. `resolve_items_unique_path(manifest_path)`
- 从 `manifest.json` 定位同目录下的 `items.unique.json`

3. `validate_manifest_for_export(manifest)`
- 校验所有任务都已经 `fetched`

4. `write_lua_item_id_table(manifest_path, output_path=None)`
- 读取 `manifest.json`
- 校验运行是否完整
- 再读取 `items.unique.json`
- 写出 Lua 文件

## 调用方式

```bash
cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler
python3 -m scripts.export_lua outputs/<run_id>/manifest.json
```

## 测试策略

- Lua 文本格式正确
- `itemId` 升序输出
- 仅完整 manifest 可导出
- `failed` 和 `planned` 会阻止导出
- 能写到插件目录
- `.toc` 已接入新文件
