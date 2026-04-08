# Tavily Search CLI

**LLM-Native CLI** — A command-line interface designed for LLM agents (Cursor, Claude, etc.) to invoke directly for web search and content extraction. Output in table, JSON, or Markdown for easy consumption by AI workflows.

## Key Features

- **Multi-Key Automatic Rotation** — Use multiple Tavily API keys with automatic day-based rotation to distribute load and avoid rate limits (1000 requests/day per key)
- **LLM-Native Output** — Table, JSON, or Markdown formats designed for AI agent consumption
- **Web Search** — Basic, advanced, fast, and ultra-fast search with rich filtering
- **Content Extraction** — Extract and parse content from any URL
- **Website Crawling** — Intelligent website crawling with depth and breadth control
- **Deep Research** — Async long-form research with citation support

## Configuration (Required)

You must configure API keys before use. Get your API keys from [tavily.com](https://tavily.com).

### JSON Config File

1. Copy the sample config file to your home directory:
   ```bash
   mkdir -p ~/.config/tavily
   cp keys.json.sample ~/.config/tavily/keys.json
   ```

2. Edit `~/.config/tavily/keys.json` and replace the placeholder keys with your actual Tavily API keys.

### Multi-Key Rotation

The CLI automatically rotates between API keys based on the day of the month:
- Days are evenly distributed across available keys
- Each key gets approximately the same number of days

**Example with 3 keys:**
- Days 1-10 → Key 1, Days 11-20 → Key 2, Days 21-31 → Key 3

This ensures you can make up to 1000 × N requests per day with N keys.

## Installation

### Using uv (Recommended)

```bash
uv tool install https://github.com/socamalo/tavily-cli
```

### Using pipx

```bash
pipx install local-tavily
```

### From source

```bash
git clone https://github.com/socamalo/tavily-cli.git
cd tavily-cli
uv tool install .
```

## CLI Commands

### tavily search

Web search with rich filtering options.

```bash
tavily search "Python programming"
tavily search "AI news" --depth advanced --max-results 20
tavily search "tech news" --topic news --time-range week
tavily search "Python" --include-domains python.org,github.com --country us
tavily search "query" --output json
```

**Options:**
- `--depth [basic|advanced|fast|ultra-fast]` - Search depth (default: basic)
- `--max-results INTEGER` - Maximum results 1-20 (default: 10)
- `--topic [general|news|finance]` - Search topic category
- `--time-range [day|week|month|year]` - Time range filter
- `--start-date TEXT` - Start date in YYYY-MM-DD format
- `--end-date TEXT` - End date in YYYY-MM-DD format
- `--days INTEGER` - Number of days back (only with topic=news)
- `--country TEXT` - Country code (e.g., us, uk, cn)
- `--include-domains TEXT` - Comma-separated domains to include
- `--exclude-domains TEXT` - Comma-separated domains to exclude
- `--include-answer / --no-include-answer` - Include AI-generated answer
- `--include-images` - Include images in results
- `--include-image-descriptions` - Include image descriptions
- `--include-raw-content` - Include raw HTML content
- `--include-favicon` - Include website favicons
- `--chunks-per-source INTEGER` - Chunks per source 1-3 (advanced only)
- `--timeout INTEGER` - Request timeout in seconds
- `-o, --output [table|json|markdown]` - Output format

### tavily extract

Extract content from URLs.

```bash
tavily extract https://example.com
tavily extract https://site1.com https://site2.com --depth advanced
tavily extract https://example.com --format markdown --output json
```

**Options:**
- `--depth [basic|advanced]` - Extract depth (default: basic)
- `--format [markdown|text]` - Output format (default: markdown)
- `--include-images` - Include images in extraction
- `--include-favicon` - Include website favicons
- `--timeout FLOAT` - Timeout in seconds for each URL
- `--query TEXT` - Query for reranking extracted content
- `--chunks-per-source INTEGER` - Chunks per source 1-5
- `-o, --output [table|json|markdown]` - Output format

### tavily crawl

Crawl a website with intelligent traversal.

```bash
tavily crawl https://docs.python.org --limit 10
tavily crawl https://example.com --instructions "find all API documentation"
tavily crawl https://example.com --max-depth 3 --allow-external
```

**Options:**
- `--instructions TEXT` - Natural language instructions for crawling
- `--max-depth INTEGER` - Maximum crawl depth 1-5
- `--max-breadth INTEGER` - Maximum breadth per level 1-500
- `--limit INTEGER` - Total links to process
- `--select-paths TEXT` - Comma-separated regex patterns for paths to include
- `--select-domains TEXT` - Comma-separated regex patterns for domains to include
- `--exclude-paths TEXT` - Comma-separated regex patterns for paths to exclude
- `--exclude-domains TEXT` - Comma-separated regex patterns for domains to exclude
- `--allow-external / --no-allow-external` - Allow external links (default: false)
- `--include-images` - Include images in results
- `--extract-depth [basic|advanced]` - Extract depth (default: basic)
- `--format [markdown|text]` - Output format (default: markdown)
- `--include-favicon` - Include website favicons
- `--timeout FLOAT` - Timeout in seconds 10-150
- `-o, --output [table|json|markdown]` - Output format

### tavily map

Map website structure (sitemap-like URL discovery).

```bash
tavily map https://docs.python.org --limit 20
tavily map https://example.com --instructions "find all blog posts"
```

**Options:**
- `--instructions TEXT` - Natural language instructions for mapping
- `--max-depth INTEGER` - Maximum map depth 1-5
- `--max-breadth INTEGER` - Maximum breadth per level 1-500
- `--limit INTEGER` - Total links to process
- `--select-paths TEXT` - Comma-separated regex patterns for paths to include
- `--select-domains TEXT` - Comma-separated regex patterns for domains to include
- `--exclude-paths TEXT` - Comma-separated regex patterns for paths to exclude
- `--exclude-domains TEXT` - Comma-separated regex patterns for domains to exclude
- `--allow-external / --no-allow-external` - Allow external links (default: false)
- `--timeout FLOAT` - Timeout in seconds 10-150
- `-o, --output [table|json|markdown]` - Output format

### tavily research

Create a deep research task (async).

```bash
tavily research "AI impact on software engineering jobs"
tavily research "climate change technology" --model pro --output json
```

**Options:**
- `--model [mini|pro|auto]` - Model to use (default: auto)
- `--citation-format [numbered|mla|apa|chicago]` - Citation format (default: numbered)
- `--output-schema JSON` - JSON Schema for structured output
- `-o, --output [table|json|markdown]` - Output format

### tavily research-status

Check the status of a research task.

```bash
tavily research-status <request_id>
tavily research-status abc123 --output json
```

**Options:**
- `-o, --output [table|json|markdown]` - Output format

### tavily usage

Get API usage information and sync all keys to local config.

```bash
tavily usage
tavily usage --output json
```

**Options:**
- `-o, --output [table|json]` - Output format (default: table)

### tavily config

Show current configuration and all key statuses.

```bash
tavily config
```

### tavily version

Show version information.

```bash
tavily version
```

## Tavily Workspace & Skills

This project includes a **Tavily workspace skill** for AI agents (such as Cursor and Claude) to call the CLI directly.

- **Skill location**: `skills/tavily/SKILL.md`
- **Purpose**: Exposes `tavily` commands (search, research, extract, crawl, map, usage, config) as an AI-friendly tool interface.
- **Default behavior**: All skill commands use `--output json` so agents can reliably parse structured results.

### Using the Tavily Skill in AI Workspaces

- **Cursor / Claude**: Add this repository (or the published package) as a workspace/tool source, then enable the `tavily` skill.
- **Typical agent commands**:
  - `/tavily search "<query>"` — Web search with filters and time ranges
  - `/tavily research "<topic>"` — Long‑form, async research jobs
  - `/tavily extract <url>` — Structured content extraction
  - `/tavily crawl <url> --limit N` — Small website crawls
  - `/tavily map <url> --limit N` — URL discovery / sitemap‑like mapping
  - `/tavily usage` / `/tavily config` — Inspect API usage and configuration

### Skill Evaluation (Claude)

The `tavily` skill has been evaluated with automated agents and **passed all tested workflows**:

- **basic-search**: `tavily search "OpenAI GPT-5 latest news"` → 10 relevant results ✅
- **search-with-filters**: `tavily search --include-domains --days 30` → filters applied correctly ✅
- **deep-research**: `tavily research "AI impact on software engineering jobs"` → research job started ✅
- **extract-content**: `tavily extract https://en.wikipedia.org/wiki/Artificial_intelligence` → full article extracted ✅
- **crawl-website**: `tavily crawl https://docs.python.org/3/tutorial/ --limit 5` → 5 pages crawled ✅
- **map-website**: `tavily map https://docs.python.org --limit 20` → 14 URLs discovered ✅
- **check-usage**: `tavily usage` → API keys / usage info returned ✅
- **view-config**: `tavily config` → configuration displayed correctly ✅

These results confirm the skill is production‑ready for LLM agents.

## Development

```bash
# Clone
git clone https://github.com/socamalo/tavily-cli.git
cd tavily-cli

# Install dependencies
uv sync

# Install in editable mode
uv pip install -e .

# Run tests
pytest tests/

# Run with coverage
pytest --cov=local_tavily tests/
```

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager (for `uv tool install`)
- Tavily API keys - Get them from [tavily.com](https://tavily.com)

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [Tavily](https://tavily.com) - Internet search engine backend
