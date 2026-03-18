# Zero Result Pages Design

**Goal:** Treat Wowhead item pages with zero matching results as successful empty fetches instead of parser failures.

**Approach:** Keep the current `listviewitems` parsing path for non-empty result pages, but add a second explicit path for zero-result pages. When the HTML contains Wowhead's empty-state marker, `parse_items_from_html()` should return an empty list instead of raising `未找到 listviewitems 数据`.

**Behavior:**
- Non-empty pages: unchanged, still parse `var listviewitems = [...]`
- Zero-result pages: return `[]`
- Truly malformed pages with neither data nor empty-state marker: still raise an error

**Scope:** This change only fixes zero-result handling. It intentionally does not address the separate `json.loads` failure on pages whose `listviewitems` payload is JavaScript object syntax rather than strict JSON.
