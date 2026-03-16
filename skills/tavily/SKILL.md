---
name: tavily
description: |
  Execute Tavily CLI commands for AI-powered web search, deep research, content extraction, and website crawling.
  Use this skill when the user wants to: search the web, find current information, research a topic deeply,
  extract content from URLs, crawl websites, map site structures, or check Tavily API usage.
  This skill is essential for any web-based research, current events, or gathering information from online sources.
  Always use this skill for search queries, research tasks, URL content extraction, or website analysis.
---

# Tavily CLI Skill

Execute Tavily CLI commands for AI-powered web search and research.

## Available Commands

### Search

Search the web with AI-powered results.

**Usage:**
- `/tavily search <query>` - Basic search
- `/tavily search <query> --depth basic|advanced` - Control search depth
- `/tavily search <query> --days <n>` - Limit results to last n days
- `/tavily search <query> --domains example.com,another.com` - Filter by domains
- `/tavily search <query> --exclude-domains spam.com` - Exclude domains

**Examples:**
```
/tavily search "latest React features"
/tavily search "climate change news" --days 7 --depth advanced
/tavily search "Python tutorials" --domains realpython.com,python.org
```

### Research

Launch deep research tasks that run asynchronously.

**Usage:**
- `/tavily research "<topic>"` - Start a research task
- `/tavily research "<topic>" --depth basic|advanced` - Control research depth
- `/tavily research "<topic>" --days <n>` - Limit to recent content

**Examples:**
```
/tavily research "quantum computing applications in healthcare"
/tavily research "renewable energy trends 2024" --depth advanced --days 30
```

**Note:** Research tasks are async. Use `/tavily research-status <job-id>` to check progress.

### Research Status

Check the status of an async research task.

**Usage:**
- `/tavily research-status <job-id>` - Get status and results

### Extract

Extract content from URLs.

**Usage:**
- `/tavily extract <url>` - Extract content from a single URL
- `/tavily extract <url1> <url2> ...` - Extract from multiple URLs

**Examples:**
```
/tavily extract https://example.com/article
/tavily extract https://site.com/page1 https://site.com/page2
```

### Crawl

Crawl a website and extract content.

**Usage:**
- `/tavily crawl <url>` - Crawl a website
- `/tavily crawl <url> --limit <n>` - Limit number of pages

**Examples:**
```
/tavily crawl https://docs.python.org
/tavily crawl https://blog.example.com --limit 10
```

### Map

Map a website's structure.

**Usage:**
- `/tavily map <url>` - Map website structure
- `/tavily map <url> --limit <n>` - Limit number of URLs

**Examples:**
```
/tavily map https://example.com
/tavily map https://docs.python.org --limit 50
```

### Usage

Check API usage statistics.

**Usage:**
- `/tavily usage` - Show current usage

### Config

View current configuration.

**Usage:**
- `/tavily config` - Show config

## Default Parameters

All commands use `--output json` for structured data parsing.

## Setup Requirements

Requires Tavily CLI to be installed and configured:
```bash
pip install tavily
# Set API key via one of:
# 1. tavily config --api-key YOUR_KEY
# 2. Environment variable: TAVILY_API_KEY=your_key
```

## Command Mapping

| Skill Command | Tavily CLI Equivalent |
|--------------|----------------------|
| `/tavily search <q>` | `tavily search "<q>" --output json` |
| `/tavily research <t>` | `tavily research "<t>" --output json` |
| `/tavily research-status <id>` | `tavily research-status <id> --output json` |
| `/tavily extract <url>` | `tavily extract <url> --output json` |
| `/tavily crawl <url>` | `tavily crawl <url> --output json` |
| `/tavily map <url>` | `tavily map <url> --output json` |
| `/tavily usage` | `tavily usage --output json` |
| `/tavily config` | `tavily config` |

## Error Handling

- If Tavily CLI is not installed, suggest: `pip install tavily`
- If API key is missing, suggest: `tavily config --api-key YOUR_KEY`
- All errors are returned with stderr for debugging
