"""
Output formatters for CLI results.

This module provides functions to format search, extract, crawl, map, research, and usage results
in different output formats: table, JSON, and markdown.
"""

import json
from typing import Any, Dict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

console = Console()


def format_search_table(results: Dict[str, Any], query: str) -> None:
    """Format search results as a rich table."""
    if results.get("status") != "success":
        console.print(f"[red]Error:[/red] {results.get('message', 'Unknown error')}")
        return

    # Print query info
    response_time = results.get("response_time", 0)
    console.print(Panel(
        f"[bold]Query:[/bold] {query}\n"
        f"[dim]Response time: {response_time}s[/dim]"
    ))

    # Print answer if available
    answer = results.get("answer")
    if answer:
        console.print(Panel(answer, title="AI Answer", border_style="green"))

    # Print results in a table
    search_results = results.get("results", [])
    if search_results:
        table = Table(title="Search Results", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="cyan", no_wrap=False)
        table.add_column("Source", style="blue")
        table.add_column("Score", justify="right", style="green")

        for i, result in enumerate(search_results, 1):
            title = result.get("title", "No title")[:60]
            url = result.get("url", "")[:40]
            score = f"{result.get('score', 0):.2f}"
            table.add_row(str(i), title, url, score)

        console.print(table)

        # Print content snippets
        console.print("\n[bold]Content Snippets:[/bold]\n")
        for i, result in enumerate(search_results, 1):
            content = result.get("content", "")
            if content:
                console.print(f"[cyan]{i}.[/cyan] [bold]{result.get('title', 'No title')}[/bold]")
                console.print(f"   [dim]{content[:200]}...[/dim]\n")

    # Print images if available
    images = results.get("images", [])
    if images:
        console.print(f"\n[dim]Found {len(images)} images[/dim]")

    # Print usage if available
    usage = results.get("usage")
    if usage:
        console.print(f"\n[dim]Usage: {usage}[/dim]")


def format_search_json(results: Dict[str, Any]) -> str:
    """Format search results as JSON."""
    return json.dumps(results, indent=2, ensure_ascii=False)


def format_search_markdown(results: Dict[str, Any], query: str) -> str:
    """Format search results as Markdown."""
    if results.get("status") != "success":
        return f"**Error:** {results.get('message', 'Unknown error')}"

    lines = []
    lines.append(f"# Search Results: {query}")
    lines.append("")
    lines.append(f"*Response time: {results.get('response_time', 0)}s*")
    lines.append("")

    # Add answer if available
    answer = results.get("answer")
    if answer:
        lines.append("## AI Answer")
        lines.append("")
        lines.append(answer)
        lines.append("")
        lines.append("---")
        lines.append("")

    # Add results
    search_results = results.get("results", [])
    if search_results:
        lines.append("## Results")
        lines.append("")

        for i, result in enumerate(search_results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            score = result.get("score", 0)
            content = result.get("content", "")

            lines.append(f"### {i}. {title}")
            lines.append("")
            lines.append(f"**URL:** [{url}]({url})")
            lines.append("")
            lines.append(f"**Score:** {score:.2f}")
            lines.append("")
            if content:
                lines.append(content[:500])
            lines.append("")
            lines.append("---")
            lines.append("")

    # Add images if available
    images = results.get("images", [])
    if images:
        lines.append("## Images")
        lines.append("")
        lines.append(f"Found {len(images)} images.")
        lines.append("")

    # Add usage if available
    usage = results.get("usage")
    if usage:
        lines.append("## Usage")
        lines.append("")
        lines.append(f"```json\n{json.dumps(usage, indent=2)}\n```")
        lines.append("")

    return "\n".join(lines)


def format_extract_table(results: Dict[str, Any], output_format: str = "markdown") -> None:
    """Format extraction results as a rich table."""
    if results.get("status") != "success":
        console.print(f"[red]Error:[/red] {results.get('message', 'Unknown error')}")
        return

    # Print successful extractions
    for result in results.get("results", []):
        url = result.get("url", "")
        content = result.get("content", "")
        raw_content = result.get("raw_content", "")

        display_content = raw_content if raw_content else content

        if output_format == "text":
            # Strip markdown for text output
            display_content = display_content.replace("#", "").replace("**", "")

        console.print(Panel(
            display_content[:2000] if len(display_content) > 2000 else display_content,
            title=f"[bold]{url}[/bold]",
            border_style="green"
        ))

    # Print failed extractions
    for failed in results.get("failed_results", []):
        url = failed.get("url", "")
        error = failed.get("error", "Unknown error")
        console.print(Panel(
            f"[red]{error}[/red]",
            title=f"[bold]{url}[/bold]",
            border_style="red"
        ))

    # Print usage if available
    usage = results.get("usage")
    if usage:
        console.print(f"\n[dim]Usage: {usage}[/dim]")


def format_extract_json(results: Dict[str, Any]) -> str:
    """Format extraction results as JSON."""
    return json.dumps(results, indent=2, ensure_ascii=False)


def format_extract_markdown(results: Dict[str, Any]) -> str:
    """Format extraction results as Markdown."""
    if results.get("status") != "success":
        return f"**Error:** {results.get('message', 'Unknown error')}"

    lines = []
    lines.append("# Extracted Content")
    lines.append("")
    lines.append(f"*Response time: {results.get('response_time', 0)}s*")
    lines.append("")

    # Add successful extractions
    for result in results.get("results", []):
        url = result.get("url", "")
        content = result.get("content", "")
        raw_content = result.get("raw_content", "")

        display_content = raw_content if raw_content else content

        lines.append(f"## {url}")
        lines.append("")
        lines.append(display_content)
        lines.append("")
        lines.append("---")
        lines.append("")

    # Add failed extractions
    for failed in results.get("failed_results", []):
        url = failed.get("url", "")
        error = failed.get("error", "Unknown error")

        lines.append(f"## {url} (FAILED)")
        lines.append("")
        lines.append(f"**Error:** {error}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Add usage if available
    usage = results.get("usage")
    if usage:
        lines.append("## Usage")
        lines.append("")
        lines.append(f"```json\n{json.dumps(usage, indent=2)}\n```")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Crawl Formatters
# =============================================================================


def format_crawl_table(results: Dict[str, Any]) -> None:
    """Format crawl results as a rich table."""
    if results.get("status") != "success":
        console.print(f"[red]Error:[/red] {results.get('message', 'Unknown error')}")
        return

    url = results.get("url", "")
    response_time = results.get("response_time", 0)

    console.print(Panel(
        f"[bold]Crawled URL:[/bold] {url}\n"
        f"[dim]Response time: {response_time}s[/dim]",
        title="Crawl Results",
        border_style="blue"
    ))

    # Print crawled pages
    crawl_results = results.get("results", [])
    if crawl_results:
        console.print(f"\n[bold]Crawled {len(crawl_results)} pages:[/bold]\n")

        for i, result in enumerate(crawl_results, 1):
            page_url = result.get("url", "")
            title = result.get("title", "No title")
            content = result.get("content", "")[:500]

            console.print(Panel(
                f"[bold]{title}[/bold]\n"
                f"[blue]{page_url}[/blue]\n\n"
                f"[dim]{content}...[/dim]",
                title=f"[cyan]Page {i}[/cyan]",
                border_style="green"
            ))

    # Print usage if available
    usage = results.get("usage")
    if usage:
        console.print(f"\n[dim]Usage: {usage}[/dim]")


def format_crawl_json(results: Dict[str, Any]) -> str:
    """Format crawl results as JSON."""
    return json.dumps(results, indent=2, ensure_ascii=False)


def format_crawl_markdown(results: Dict[str, Any]) -> str:
    """Format crawl results as Markdown."""
    if results.get("status") != "success":
        return f"**Error:** {results.get('message', 'Unknown error')}"

    lines = []
    lines.append("# Crawl Results")
    lines.append("")
    lines.append(f"**URL:** {results.get('url', '')}")
    lines.append("")
    lines.append(f"*Response time: {results.get('response_time', 0)}s*")
    lines.append("")

    # Add crawled pages
    crawl_results = results.get("results", [])
    if crawl_results:
        lines.append(f"## Crawled {len(crawl_results)} pages")
        lines.append("")

        for i, result in enumerate(crawl_results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "")

            lines.append(f"### {i}. {title}")
            lines.append("")
            lines.append(f"**URL:** [{url}]({url})")
            lines.append("")
            if content:
                lines.append(content[:1000])
            lines.append("")
            lines.append("---")
            lines.append("")

    # Add usage if available
    usage = results.get("usage")
    if usage:
        lines.append("## Usage")
        lines.append("")
        lines.append(f"```json\n{json.dumps(usage, indent=2)}\n```")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Map Formatters
# =============================================================================


def format_map_table(results: Dict[str, Any]) -> None:
    """Format map results as a rich table."""
    if results.get("status") != "success":
        console.print(f"[red]Error:[/red] {results.get('message', 'Unknown error')}")
        return

    url = results.get("url", "")
    response_time = results.get("response_time", 0)

    console.print(Panel(
        f"[bold]Mapped URL:[/bold] {url}\n"
        f"[dim]Response time: {response_time}s[/dim]",
        title="Map Results",
        border_style="blue"
    ))

    # Print mapped links
    map_results = results.get("results", [])
    if map_results:
        console.print(f"\n[bold]Found {len(map_results)} links:[/bold]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=5)
        table.add_column("URL", style="cyan")

        for i, link in enumerate(map_results, 1):
            table.add_row(str(i), link)

        console.print(table)

    # Print usage if available
    usage = results.get("usage")
    if usage:
        console.print(f"\n[dim]Usage: {usage}[/dim]")


def format_map_json(results: Dict[str, Any]) -> str:
    """Format map results as JSON."""
    return json.dumps(results, indent=2, ensure_ascii=False)


def format_map_markdown(results: Dict[str, Any]) -> str:
    """Format map results as Markdown."""
    if results.get("status") != "success":
        return f"**Error:** {results.get('message', 'Unknown error')}"

    lines = []
    lines.append("# Map Results")
    lines.append("")
    lines.append(f"**URL:** {results.get('url', '')}")
    lines.append("")
    lines.append(f"*Response time: {results.get('response_time', 0)}s*")
    lines.append("")

    # Add mapped links
    map_results = results.get("results", [])
    if map_results:
        lines.append(f"## Found {len(map_results)} links")
        lines.append("")

        for i, link in enumerate(map_results, 1):
            lines.append(f"{i}. [{link}]({link})")

        lines.append("")

    # Add usage if available
    usage = results.get("usage")
    if usage:
        lines.append("## Usage")
        lines.append("")
        lines.append(f"```json\n{json.dumps(usage, indent=2)}\n```")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Research Formatters
# =============================================================================


def format_research_table(results: Dict[str, Any]) -> None:
    """Format research results as a rich table."""
    if results.get("status") != "success":
        console.print(f"[red]Error:[/red] {results.get('message', 'Unknown error')}")
        return

    request_id = results.get("request_id", "")
    state = results.get("state", "")

    console.print(Panel(
        f"[bold]Request ID:[/bold] {request_id}\n"
        f"[bold]State:[/bold] {state or 'completed'}\n"
        f"[dim]Response time: {results.get('response_time', 0)}s[/dim]",
        title="Research Results",
        border_style="blue"
    ))

    # Print result if available
    result = results.get("result")
    if result:
        if isinstance(result, str):
            console.print(Panel(result, title="Research Output", border_style="green"))
        else:
            console.print(Panel(
                json.dumps(result, indent=2, ensure_ascii=False),
                title="Research Output",
                border_style="green"
            ))

    # Print error if available
    error = results.get("error")
    if error:
        console.print(Panel(f"[red]{error}[/red]", title="Error", border_style="red"))


def format_research_json(results: Dict[str, Any]) -> str:
    """Format research results as JSON."""
    return json.dumps(results, indent=2, ensure_ascii=False)


def format_research_markdown(results: Dict[str, Any]) -> str:
    """Format research results as Markdown."""
    if results.get("status") != "success":
        return f"**Error:** {results.get('message', 'Unknown error')}"

    lines = []
    lines.append("# Research Results")
    lines.append("")
    lines.append(f"**Request ID:** {results.get('request_id', '')}")
    if results.get("state"):
        lines.append(f"**State:** {results.get('state')}")
    if results.get("model"):
        lines.append(f"**Model:** {results.get('model')}")
    lines.append("")
    lines.append(f"*Response time: {results.get('response_time', 0)}s*")
    lines.append("")

    # Add result if available
    result = results.get("result")
    if result:
        lines.append("## Result")
        lines.append("")
        if isinstance(result, str):
            lines.append(result)
        else:
            lines.append(f"```json\n{json.dumps(result, indent=2)}\n```")
        lines.append("")

    # Add error if available
    error = results.get("error")
    if error:
        lines.append("## Error")
        lines.append("")
        lines.append(f"**{error}**")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# Usage Formatters
# =============================================================================


def format_usage_table(results: Dict[str, Any]) -> None:
    """Format usage results as a rich table."""
    if results.get("status") != "success":
        console.print(f"[red]Error:[/red] {results.get('message', 'Unknown error')}")
        return

    usage = results.get("usage", {})

    console.print(Panel(
        "[bold]API Usage Information[/bold]",
        title="Usage",
        border_style="blue"
    ))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    # Flatten usage data
    for key, value in usage.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                table.add_row(f"{key}.{sub_key}", str(sub_value))
        else:
            table.add_row(key, str(value))

    console.print(table)


def format_usage_json(results: Dict[str, Any]) -> str:
    """Format usage results as JSON."""
    return json.dumps(results, indent=2, ensure_ascii=False)
