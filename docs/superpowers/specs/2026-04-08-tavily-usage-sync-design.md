# Tavily Usage Sync Design

## Problem

`tavily usage` currently only checks the active key and does not sync API usage data back to `keys.json`.

## Goals

1. Check all keys in `keys.json` by calling Tavily `/usage` API for each key
2. Sync API-returned `key.usage` to local `keys.json` (overwrite)
3. Auto-enable keys that are under quota in API but marked disabled locally
4. Clear errors array when usage is synced (indicates usage was reset)
5. Report sync status to user

## Architecture

### New Functions (`src/local_tavily/usage.py`)

**`fetch_key_usage(api_key: str) -> tuple[bool, dict | None, str | None]`**
- Calls `GET https://api.tavily.com/usage` with Bearer token
- Returns `(success, usage_data, error_message)`
- usage_data contains the `key.*` fields from API response

**`sync_all_keys_usage() -> dict`**
- Iterates all keys from key_manager
- Calls `fetch_key_usage()` for each key
- Updates `keys.json`: sets `usage` from API, `disabled` based on quota, clears `errors`
- Returns `{updated: [key_names], failed: [(key_name, error)], total: N}`

**`tavily_usage() -> dict`**
- Calls `sync_all_keys_usage()` to sync and get results
- Returns merged data: API account-level data + sync status

### CLI Changes (`src/local_tavily/cli.py`)

- Show "Syncing..." progress indicator
- Execute `tavily_usage()` (which now syncs internally)
- Display API data table (unchanged)
- Show "Synced X/Y keys" final report
- List any failed keys with errors

## Data Flow

```
tavily usage
  → tavily_usage()
    → sync_all_keys_usage()
      → for each key in keys.json:
        → fetch_key_usage(key) → GET /usage
    → update keys.json (usage=API value, disabled=<1000, errors=[])
    → save
  → return {account_data, sync_result}
  → CLI display table + sync report
```

## Sync Rules

| API `key.usage` | Local `disabled` | Action |
|-----------------|-------------------|--------|
| < 1000 | true | Set `disabled: false` |
| >= 1000 | false | Set `disabled: true` |
| any | any | Set `usage` from API, clear `errors` |
| null/missing | unchanged | Skip this key |

## Error Handling

- Single key fails → skip, continue with others, report at end
- All keys fail → raise error, no changes to local file
- Partial success → update successful keys, report failures

## Out of Scope

- Batch API endpoint (not available)
- Adding unknown keys to local config
- Manual quota configuration
