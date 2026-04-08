"""
Command-line interface for Local Tavily.

This module provides a comprehensive CLI for interacting with the Tavily API
directly from the command line, supporting search, extract, crawl, map, research, and usage commands.
"""

import os
import sys
from typing import List, Optional

# Fix Windows encoding issues
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import click
from dotenv import load_dotenv
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


# Load environment variables from .env file
# Search in multiple locations: current dir, package dir, user config dir, home dir
def _load_env_files():
    """Load .env from multiple possible locations.

    Priority order:
    1. Current working directory (project-specific settings)
    2. Package installation directory (for bundled configs)
    3. XDG config directory (~/.config/tavily/.env)
    4. User config directory (~/.config/.env)
    5. Home directory (~/.tavily.env)

    All found files are loaded, with later ones overriding earlier ones.
    """
    loaded_any = False
    env_paths = []

    # 1. Current working directory
    env_paths.append(Path.cwd() / ".env")

    # 2. Package directory (for uv tool install global installs)
    package_dir = Path(__file__).parent
    env_paths.append(package_dir / ".env")

    # 3. XDG config directory (standard location)
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        env_paths.append(Path(xdg_config) / "tavily" / ".env")
    env_paths.append(Path.home() / ".config" / "tavily" / ".env")

    # 4. User config directory (alternative)
    env_paths.append(Path.home() / ".config" / ".env")

    # 5. Home directory as fallback
    env_paths.append(Path.home() / ".tavily.env")

    # Load each file if it exists
    for env_path in env_paths:
        if env_path.exists():
            try:
                load_dotenv(env_path, override=True)
                loaded_any = True
            except Exception:
                pass  # Silently ignore unreadable files

    return loaded_any


# Load env files immediately on module import
_load_env_files()

from local_tavily import __version__
from local_tavily.key_manager import TavilyKeyManager, get_key_manager, NoAvailableKeyError
from local_tavily.search import tavily_search
from local_tavily.extract import tavily_extract
from local_tavily.crawl import tavily_crawl
from local_tavily.map import tavily_map
from local_tavily.research import tavily_research, tavily_research_status
from local_tavily.usage import tavily_usage
from local_tavily.formatters import (
    format_search_table,
    format_search_json,
    format_search_markdown,
    format_extract_table,
    format_extract_json,
    format_extract_markdown,
    format_crawl_table,
    format_crawl_json,
    format_crawl_markdown,
    format_map_table,
    format_map_json,
    format_map_markdown,
    format_research_table,
    format_research_json,
    format_research_markdown,
    format_usage_table,
    format_usage_json,
)

console = Console()


def get_api_key() -> str:
    """Get the current API key from the key manager."""
    try:
        return get_key_manager().get_key()
    except NoAvailableKeyError as e:
        raise click.ClickException(str(e))


def validate_api_key():
    """Validate that API keys are configured."""
    try:
        get_key_manager().get_key()
    except NoAvailableKeyError as e:
        raise click.ClickException(str(e))


def parse_comma_separated(value: Optional[str]) -> Optional[List[str]]:
    """Parse comma-separated string into list."""
    if not value:
        return None
    return [item.strip() for item in value.split(",")]


@click.group()
@click.version_option(version=__version__, prog_name="tavily")
def cli():
    """Tavily Search CLI - AI-powered web search from the command line."""
    pass


@cli.command()
@click.argument('query')
@click.option('--depth', type=click.Choice(['basic', 'advanced', 'fast', 'ultra-fast']), default='basic',
              help='Search depth: basic, advanced, fast, or ultra-fast')
@click.option('--max-results', type=click.IntRange(0, 20), default=10,
              help='Maximum number of results (0-20)')
@click.option('--topic', type=click.Choice(['general', 'news', 'finance']), default='general',
              help='Search topic category')
@click.option('--time-range', type=click.Choice(['day', 'week', 'month', 'year', 'd', 'w', 'm', 'y']),
              help='Time range for results (day/week/month/year or d/w/m/y)')
@click.option('--start-date', help='Start date in YYYY-MM-DD format')
@click.option('--end-date', help='End date in YYYY-MM-DD format')
@click.option('--days', type=int, help='Number of days back (only works with topic=news)')
@click.option('--country', help='Country code (e.g., us, uk, cn) or full name (e.g., "United States")')
@click.option('--include-domains', help='Comma-separated list of domains to include')
@click.option('--exclude-domains', help='Comma-separated list of domains to exclude')
@click.option('--include-answer', default='true',
              help='Include AI-generated answer (true/false/basic/advanced)')
@click.option('--include-images', is_flag=True, help='Include images in results')
@click.option('--include-image-descriptions', is_flag=True, help='Include image descriptions')
@click.option('--include-raw-content', default='false',
              help='Include raw content (true/false/markdown/text)')
@click.option('--include-favicon', is_flag=True, help='Include website favicons')
@click.option('--chunks-per-source', type=click.IntRange(1, 3),
              help='Number of chunks per source (1-3, only with advanced depth)')
@click.option('--timeout', type=int, default=60, help='Request timeout in seconds (default: 60)')
@click.option('--auto-parameters', is_flag=True, help='Automatically configure search parameters')
@click.option('--exact-match', is_flag=True, help='Use exact matching for search query')
@click.option('--include-usage', is_flag=True, help='Include usage statistics in response')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'markdown']), default='table',
              help='Output format')
def search(
    query: str,
    depth: str,
    max_results: int,
    topic: str,
    time_range: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    days: Optional[int],
    country: Optional[str],
    include_domains: Optional[str],
    exclude_domains: Optional[str],
    include_answer: str,
    include_images: bool,
    include_image_descriptions: bool,
    include_raw_content: str,
    include_favicon: bool,
    chunks_per_source: Optional[int],
    timeout: int,
    auto_parameters: bool,
    exact_match: bool,
    include_usage: bool,
    output: str,
):
    """Search the web using Tavily."""
    validate_api_key()

    # Parse domain lists
    include_domains_list = parse_comma_separated(include_domains)
    exclude_domains_list = parse_comma_separated(exclude_domains)

    # Parse include_answer - can be bool or enum (true/false/basic/advanced)
    include_answer_lower = include_answer.lower()
    if include_answer_lower in ('true', '1', 'yes'):
        include_answer_val = True
    elif include_answer_lower in ('false', '0', 'no'):
        include_answer_val = False
    elif include_answer_lower in ('basic', 'advanced'):
        include_answer_val = include_answer_lower  # "basic" or "advanced"
    else:
        raise click.ClickException(
            f"Invalid --include-answer value: '{include_answer}'. "
            "Must be one of: true, false, basic, advanced"
        )

    # Parse include_raw_content - can be bool or enum (true/false/markdown/text)
    include_raw_lower = include_raw_content.lower()
    if include_raw_lower in ('true', '1', 'yes'):
        include_raw_content_val = True
    elif include_raw_lower in ('false', '0', 'no'):
        include_raw_content_val = False
    elif include_raw_lower in ('markdown', 'text'):
        include_raw_content_val = include_raw_lower  # "markdown" or "text"
    else:
        raise click.ClickException(
            f"Invalid --include-raw-content value: '{include_raw_content}'. "
            "Must be one of: true, false, markdown, text"
        )

    # Execute search
    results = tavily_search(
        query=query,
        search_depth=depth,
        max_results=max_results,
        topic=topic,
        time_range=time_range,
        start_date=start_date,
        end_date=end_date,
        days=days,
        country=country,
        include_domains=include_domains_list,
        exclude_domains=exclude_domains_list,
        include_answer=include_answer_val,
        include_images=include_images,
        include_image_descriptions=include_image_descriptions,
        include_raw_content=include_raw_content_val,
        include_favicon=include_favicon,
        chunks_per_source=chunks_per_source,
        timeout=timeout,
        auto_parameters=auto_parameters,
        exact_match=exact_match,
        include_usage=include_usage,
    )

    # Handle errors
    if results.get("status") != "success":
        raise click.ClickException(results.get("message", "Unknown error"))

    # Format output
    if output == "json":
        click.echo(format_search_json(results))
    elif output == "markdown":
        click.echo(format_search_markdown(results, query))
    else:  # table
        format_search_table(results, query)


@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--depth', type=click.Choice(['basic', 'advanced']), default='basic',
              help='Extract depth: basic or advanced')
@click.option('--format', 'output_format', type=click.Choice(['markdown', 'text']), default='markdown',
              help='Output format')
@click.option('--include-images', is_flag=True, help='Include images in extraction')
@click.option('--include-favicon', is_flag=True, help='Include website favicons')
@click.option('--timeout', type=float, help='Timeout in seconds for each URL')
@click.option('--query', help='Query for reranking extracted content')
@click.option('--chunks-per-source', type=click.IntRange(1, 5),
              help='Number of chunks per source (1-5, requires --query)')
@click.option('--include-usage', is_flag=True, help='Include usage statistics in response')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'markdown']), default='table',
              help='Output format')
def extract(
    urls: tuple,
    depth: str,
    output_format: str,
    include_images: bool,
    include_favicon: bool,
    timeout: Optional[float],
    query: Optional[str],
    chunks_per_source: Optional[int],
    include_usage: bool,
    output: str,
):
    """Extract content from URLs."""
    validate_api_key()

    url_list = list(urls)

    if len(url_list) > 20:
        raise click.ClickException("Maximum 20 URLs allowed per extraction request")

    # Execute extraction
    results = tavily_extract(
        urls=url_list,
        extract_depth=depth,
        format=output_format,
        include_images=include_images,
        include_favicon=include_favicon,
        timeout=timeout,
        query=query,
        chunks_per_source=chunks_per_source,
        include_usage=include_usage,
    )

    # Handle errors
    if results.get("status") != "success":
        raise click.ClickException(results.get("message", "Unknown error"))

    # Format output
    if output == "json":
        click.echo(format_extract_json(results))
    elif output == "markdown":
        click.echo(format_extract_markdown(results))
    else:  # table
        format_extract_table(results, output_format)


@cli.command()
@click.argument('url')
@click.option('--instructions', help='Natural language instructions for crawling')
@click.option('--max-depth', type=click.IntRange(1, 5), help='Maximum crawl depth (1-5)')
@click.option('--max-breadth', type=click.IntRange(1, 500), help='Maximum breadth per level (1-500)')
@click.option('--limit', type=int, help='Total links to process')
@click.option('--select-paths', help='Comma-separated regex patterns for paths to include')
@click.option('--select-domains', help='Comma-separated regex patterns for domains to include')
@click.option('--exclude-paths', help='Comma-separated regex patterns for paths to exclude')
@click.option('--exclude-domains', help='Comma-separated regex patterns for domains to exclude')
@click.option('--allow-external/--no-allow-external', default=False, help='Allow external links')
@click.option('--include-images', is_flag=True, help='Include images in results')
@click.option('--extract-depth', type=click.Choice(['basic', 'advanced']), default='basic',
              help='Extract depth: basic or advanced')
@click.option('--format', 'output_format', type=click.Choice(['markdown', 'text']), default='markdown',
              help='Output format')
@click.option('--include-favicon', is_flag=True, help='Include website favicons')
@click.option('--timeout', type=click.FloatRange(10, 150), help='Timeout in seconds (10-150)')
@click.option('--include-usage', is_flag=True, help='Include usage statistics in response')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'markdown']), default='table',
              help='Output format')
def crawl(
    url: str,
    instructions: Optional[str],
    max_depth: Optional[int],
    max_breadth: Optional[int],
    limit: Optional[int],
    select_paths: Optional[str],
    select_domains: Optional[str],
    exclude_paths: Optional[str],
    exclude_domains: Optional[str],
    allow_external: bool,
    include_images: bool,
    extract_depth: str,
    output_format: str,
    include_favicon: bool,
    timeout: Optional[float],
    include_usage: bool,
    output: str,
):
    """Crawl a website using Tavily."""
    validate_api_key()

    # Parse regex pattern lists
    select_paths_list = parse_comma_separated(select_paths)
    select_domains_list = parse_comma_separated(select_domains)
    exclude_paths_list = parse_comma_separated(exclude_paths)
    exclude_domains_list = parse_comma_separated(exclude_domains)

    # Execute crawl
    results = tavily_crawl(
        url=url,
        instructions=instructions,
        max_depth=max_depth,
        max_breadth=max_breadth,
        limit=limit,
        select_paths=select_paths_list,
        select_domains=select_domains_list,
        exclude_paths=exclude_paths_list,
        exclude_domains=exclude_domains_list,
        allow_external=allow_external,
        include_images=include_images,
        extract_depth=extract_depth,
        format=output_format,
        include_favicon=include_favicon,
        timeout=timeout,
        include_usage=include_usage,
    )

    # Handle errors
    if results.get("status") != "success":
        raise click.ClickException(results.get("message", "Unknown error"))

    # Format output
    if output == "json":
        click.echo(format_crawl_json(results))
    elif output == "markdown":
        click.echo(format_crawl_markdown(results))
    else:  # table
        format_crawl_table(results)


@cli.command()
@click.argument('url')
@click.option('--instructions', help='Natural language instructions for mapping')
@click.option('--max-depth', type=click.IntRange(1, 5), help='Maximum map depth (1-5)')
@click.option('--max-breadth', type=click.IntRange(1, 500), help='Maximum breadth per level (1-500)')
@click.option('--limit', type=int, help='Total links to process')
@click.option('--select-paths', help='Comma-separated regex patterns for paths to include')
@click.option('--select-domains', help='Comma-separated regex patterns for domains to include')
@click.option('--exclude-paths', help='Comma-separated regex patterns for paths to exclude')
@click.option('--exclude-domains', help='Comma-separated regex patterns for domains to exclude')
@click.option('--allow-external/--no-allow-external', default=False, help='Allow external links')
@click.option('--timeout', type=click.FloatRange(10, 150), help='Timeout in seconds (10-150)')
@click.option('--include-usage', is_flag=True, help='Include usage statistics in response')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'markdown']), default='table',
              help='Output format')
def map(
    url: str,
    instructions: Optional[str],
    max_depth: Optional[int],
    max_breadth: Optional[int],
    limit: Optional[int],
    select_paths: Optional[str],
    select_domains: Optional[str],
    exclude_paths: Optional[str],
    exclude_domains: Optional[str],
    allow_external: bool,
    timeout: Optional[float],
    include_usage: bool,
    output: str,
):
    """Map a website structure using Tavily."""
    validate_api_key()

    # Parse regex pattern lists
    select_paths_list = parse_comma_separated(select_paths)
    select_domains_list = parse_comma_separated(select_domains)
    exclude_paths_list = parse_comma_separated(exclude_paths)
    exclude_domains_list = parse_comma_separated(exclude_domains)

    # Execute map
    results = tavily_map(
        url=url,
        instructions=instructions,
        max_depth=max_depth,
        max_breadth=max_breadth,
        limit=limit,
        select_paths=select_paths_list,
        select_domains=select_domains_list,
        exclude_paths=exclude_paths_list,
        exclude_domains=exclude_domains_list,
        allow_external=allow_external,
        timeout=timeout,
        include_usage=include_usage,
    )

    # Handle errors
    if results.get("status") != "success":
        raise click.ClickException(results.get("message", "Unknown error"))

    # Format output
    if output == "json":
        click.echo(format_map_json(results))
    elif output == "markdown":
        click.echo(format_map_markdown(results))
    else:  # table
        format_map_table(results)


@cli.command()
@click.argument('input_text')
@click.option('--model', type=click.Choice(['mini', 'pro', 'auto']), default='auto',
              help='Model to use: mini, pro, or auto')
@click.option('--citation-format', type=click.Choice(['numbered', 'mla', 'apa', 'chicago']),
              default='numbered', help='Citation format')
@click.option('--output-schema', help='JSON Schema for structured output')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'markdown']), default='table',
              help='Output format')
def research(
    input_text: str,
    model: str,
    citation_format: str,
    output_schema: Optional[str],
    output: str,
):
    """Create a deep research task using Tavily."""
    validate_api_key()

    # Parse output schema if provided
    output_schema_dict = None
    if output_schema:
        import json
        try:
            output_schema_dict = json.loads(output_schema)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON schema: {e}")

    # Execute research
    results = tavily_research(
        input=input_text,
        model=model,
        citation_format=citation_format,
        output_schema=output_schema_dict,
    )

    # Handle errors
    if results.get("status") != "success":
        raise click.ClickException(results.get("message", "Unknown error"))

    # Format output
    if output == "json":
        click.echo(format_research_json(results))
    elif output == "markdown":
        click.echo(format_research_markdown(results))
    else:  # table
        format_research_table(results)


@cli.command('research-status')
@click.argument('request_id')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'markdown']), default='table',
              help='Output format')
def research_status(
    request_id: str,
    output: str,
):
    """Get the status of a research task."""
    validate_api_key()

    # Execute research status check
    results = tavily_research_status(request_id)

    # Handle errors
    if results.get("status") != "success":
        raise click.ClickException(results.get("message", "Unknown error"))

    # Format output
    if output == "json":
        click.echo(format_research_json(results))
    elif output == "markdown":
        click.echo(format_research_markdown(results))
    else:  # table
        format_research_table(results)


@cli.command()
@click.option('--output', '-o', type=click.Choice(['table', 'json']), default='table',
              help='Output format')
def usage(output: str):
    """Get API usage information and sync all keys to local config."""
    validate_api_key()

    # Show syncing progress
    console.print("[yellow]Syncing all keys...[/yellow]")

    # Execute usage query (which now syncs internally)
    results = tavily_usage()

    # Handle errors
    if results.get("status") != "success":
        raise click.ClickException(results.get("message", "Unknown error"))

    # Format output
    if output == "json":
        click.echo(format_usage_json(results))
    else:  # table
        format_usage_table(results)

    # Show sync result
    sync_result = results.get("sync_result", {})
    updated = sync_result.get("updated", [])
    failed = sync_result.get("failed", [])
    total = sync_result.get("total", 0)

    if failed:
        failed_names = ", ".join([f[0] for f in failed])
        console.print(f"[yellow]Synced {len(updated)}/{total} keys. Failed: {failed_names}[/yellow]")
    else:
        console.print(f"[green]Synced {len(updated)}/{total} keys successfully[/green]")


@cli.command()
def version():
    """Show version information."""
    console.print(Panel(
        f"[bold]Local Tavily[/bold]\n"
        f"Version: [cyan]{__version__}[/cyan]\n"
        f"Python: [cyan]{sys.version.split()[0]}[/cyan]",
        title="Version Info",
        border_style="blue"
    ))


@cli.command()
def config():
    """Show configuration information."""
    try:
        km = get_key_manager()
        keys_status = km.get_all_keys_status()
    except (ValueError, NoAvailableKeyError) as e:
        console.print(f"[red]Error:[/red] {e}")
        return

    table = Table(title="Configuration")
    table.add_column("Key Name", style="cyan")
    table.add_column("Usage", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Errors", style="red")

    for key_info in keys_status:
        usage = key_info["usage"]
        status = "disabled" if key_info["disabled"] else f"{usage}/1000"
        error_count = key_info["error_count"]
        masked_key = key_info["key"][:8] + "..." if len(key_info["key"]) > 12 else "***"
        table.add_row(f"{key_info['name']} ({masked_key})", str(usage), status, str(error_count))

    console.print(table)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
