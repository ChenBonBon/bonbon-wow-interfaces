# JS Object `listviewitems` Design

**Goal:** Parse Wowhead `listviewitems` payloads that are JavaScript object literals rather than strict JSON.

**Approach:** Keep the existing extraction flow, but add a small normalization step before `json.loads()`. The normalizer will quote bare object keys like `firstseenpatch: 0` and `popularity: 30`, which is the concrete format we observed in Wowhead responses. We will continue extracting only the minimal `id` and `name` fields after parsing.

**Behavior:**
- Standard JSON payloads: unchanged
- Zero-result pages: unchanged, still return `[]`
- JS object literal payloads with bare keys: normalized and parsed successfully
- Truly malformed payloads: still raise an error

**Scope:** This fix targets the currently observed Wowhead syntax mismatch only. It does not try to become a full JavaScript parser.
