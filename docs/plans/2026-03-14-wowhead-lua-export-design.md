# Wowhead Lua Export 设计

**目标：** 将 `items.unique.json` 导出为 QuickDisenchant 可直接加载的 Lua 数据文件。

## 设计原则

- 不改动现有 JSON 数据源
- 独立生成新的 Lua 文件
- 输出结构以插件运行效率为优先
- 文件内容稳定排序，避免无意义 diff

## 输入与输出

输入：

- `crawler/outputs/<run_id>/items.unique.json`

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

2. `write_lua_item_id_table(items_unique_path, output_path=None)`
- 读取 `items.unique.json`
- 写出 Lua 文件

## 调用方式

```bash
cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler
python3 -m scripts.export_lua outputs/<run_id>/items.unique.json
```

## 测试策略

- Lua 文本格式正确
- `itemId` 升序输出
- 能写到插件目录
- `.toc` 已接入新文件
