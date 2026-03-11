# Changelog

## [0.3.0] - 2026-03-05

### Changed
- **BREAKING**: Removed all MCP server functionality - this is now a pure CLI tool
- Refactored architecture with separate modules for search, extract, and formatters
- Comprehensive CLI with all Tavily API parameters supported

### Added
- `search` command with full parameter support:
  - Search depth, max results, topic filtering
  - Time range, date filtering, days back
  - Country targeting, domain filtering
  - Image options, raw content, favicon
  - Chunks per source, timeout
- `extract` command with full parameter support:
  - Multiple URL extraction
  - Extract depth, format options
  - Image and favicon extraction
  - Timeout configuration
- Multiple output formats: table (default), JSON, Markdown
- Comprehensive test suite with 63 tests
- TDD approach with tests written before implementation

### Removed
- MCP server functionality (`serve` command)
- `fastmcp` dependency
- `tavily-mcp` entry point

## [0.2.0] - 2026-03-04

### Added
- CLI interface with click
- `tavily search` command for direct search
- `tavily extract` command for URL content extraction
- `tavily serve` command for MCP server mode
- `tavily --version` command
- Comprehensive test suite
- Code coverage reporting

### Changed
- Refactored to standard Python package structure
- Improved error messages
- Better output formatting with rich

### Fixed
- Package installation with uv tool install
