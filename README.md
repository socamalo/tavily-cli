# Tavily Search CLI

**LLM-Native CLI** — A command-line interface designed for LLM agents (Cursor, Claude, etc.) to invoke directly for web search and content extraction. Output in table, JSON, or Markdown for easy consumption by AI workflows.

## Configuration (Required)

You must configure API keys before use. Choose one of the following:

1. **Edit `key_manager.py`** — Add your keys to `DEFAULT_API_KEYS` in `src/local_tavily/key_manager.py`
2. **Environment variables** — Set `TAVILY_API_KEY_1`, `TAVILY_API_KEY_2`, etc. (or `TAVILY_API_KEY` for a single key)

Get your API keys from [tavily.com](https://tavily.com).

## Features

### Key Highlights

1. **LLM-Native CLI** - Designed for AI agents to invoke directly; outputs table, JSON, or Markdown
2. **AI-Powered Search** - Advanced web search with intelligent filtering and targeting
3. **Content Extraction** - Extract and parse content from any URL
4. **Automatic Key Rotation** - Supports multiple API keys with intelligent date-based rotation to distribute load and avoid rate limits
5. **Multiple Output Formats** - Table, JSON, and Markdown output formats

### Search Capabilities

- **Basic/Advanced Search** - Choose search depth for different use cases
- **Topic Filtering** - General web search, news search, or finance search
- **Time Range** - Filter results by date ranges (day, week, month, year)
- **Domain Filtering** - Include or exclude specific websites
- **Country Targeting** - Get search results filtered by geographic location
- **Image Search** - Include images and image descriptions in results

### Extract Capabilities

- **URL Content Extraction** - Extract content from single or multiple URLs
- **Basic/Advanced Extraction** - Choose extraction depth based on your needs
- **Format Options** - Get results in Markdown or plain text format

## Installation

### Using uv (Recommended)

```bash
uv tool install local-tavily
```

### Using pipx

```bash
pipx install local-tavily
```

### From source

```bash
git clone https://github.com/yourusername/tavily-cli.git
cd tavily-cli
uv pip install -e .
```

## CLI Usage

### Search

```bash
# Basic search
tavily search "Python programming"

# Advanced search with filters
tavily search "AI news" --depth advanced --max-results 20

# News search with time range
tavily search "tech news" --topic news --time-range week

# Search with domain filtering
tavily search "Python" --include-domains python.org,github.com --country us

# Search with output format
tavily search "query" --output json
tavily search "query" --output markdown
```

#### Search Options

- `--depth [basic|advanced]` - Search depth (default: basic)
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

### Extract

```bash
# Extract from single URL
tavily extract https://example.com

# Extract from multiple URLs
tavily extract https://site1.com https://site2.com --depth advanced

# Extract with format option
tavily extract https://example.com --format markdown --output json
```

#### Extract Options

- `--depth [basic|advanced]` - Extract depth (default: basic)
- `--format [markdown|text]` - Output format (default: markdown)
- `--include-images` - Include images in extraction
- `--include-favicon` - Include website favicons
- `--timeout FLOAT` - Timeout in seconds for each URL
- `-o, --output [table|json|markdown]` - Output format

### Other Commands

```bash
# Show version
tavily version

# Show configuration
tavily config

# Show help
tavily --help
tavily search --help
tavily extract --help
```

## Configuration Details

### Environment Variables

Create a `.env` file in your project directory or home directory:

```env
# Tavily API keys
# Get your API keys from https://tavily.com
# Add multiple keys for automatic rotation to improve reliability
TAVILY_API_KEY_1=your-tavily-api-key-1
TAVILY_API_KEY_2=your-tavily-api-key-2
TAVILY_API_KEY_3=your-tavily-api-key-3
```

Or use a single API key:

```env
TAVILY_API_KEY=your-tavily-api-key
```

### Key Rotation

The CLI automatically rotates between API keys based on the day of the month:
- Days are evenly distributed across available keys
- For example, with 6 keys: each key handles approximately 5 days
- The rotation is calculated automatically based on the number of keys you provide

**Example:**
- With 6 keys: Days 1-5 → Key 1, Days 6-10 → Key 2, etc.
- With 3 keys: Days 1-10 → Key 1, Days 11-20 → Key 2, Days 21-31 → Key 3

## Development

```bash
# Clone
git clone https://github.com/yourusername/tavily-cli.git
cd tavily-cli

# Install in editable mode
uv pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=local_tavily tests/
```

## Requirements

- Python 3.10+ (as specified in `pyproject.toml`)
- [uv](https://github.com/astral-sh/uv) package manager (for `uv tool install`)
- Tavily API keys - Get them from [tavily.com](https://tavily.com)

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [Tavily](https://tavily.com) - Internet search engine backend
