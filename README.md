# UI/UX Inspo Engine (dia-mcp) 🎨

A Model Context Protocol (MCP) server that empowers AI agents to find, index, and analyze the best UI/UX visual inspiration as images from across the web.

## Overview

The UX Inspo Engine is designed to help you search for UI/UX inspiration quickly and build a local pattern index. Instead of giving you code to copy, it provides visual inspiration alongside design reasoning (why it works, what pattern it uses, what principle it demonstrates).

Built with [FastMCP](https://github.com/jlowin/fastmcp), `dia-mcp` connects LLM agents directly with tools like [Firecrawl](https://firecrawl.dev) and [TinyFish](https://tinyfish.ai) to search, screenshot, and analyze real shipped products and design platforms.

## Capabilities

The server provides several tools that AI agents can use:
- **`find_inspo`**: 🎨 Find the best UI/UX inspiration images for any design need.
- **`screenshot_live_app`**: 📸 Capture high-quality screenshots of any live application.
- **`dig_platform`**: 🕵️ Deep-dive into design platforms like Mobbin, Refero, or Godly using an AI agent.
- **`compare_uis`**: ⚖️ Screenshot and compare multiple live products side-by-side.
- **`extract_design_dna`**: 🧬 Extract design tokens, color palettes, and typography from any site.
- **`walk_flow`**: 🚶 Walk through a real multi-step UI flow and document every step.
- **`site_pattern_hunt`**: 🏹 Smartly hunt for UI/UX patterns across a whole website.
- **`index_pattern`**: 💾 Save a UI/UX pattern to the persistent Research Index.
- **`index_flow`**: 🔬 Walk through and index an entire multi-page flow.
- **`search_index`**: 🔎 Search your accumulated UI/UX Research Index.

It also includes prompts like `inspo_hunt` to kick off visual research sessions.

## Setup & Installation

This project relies on `uv` for dependency management. Requires Python 3.13+.

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd dia-mcp
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure Environment Variables:**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Add your API keys to the `.env` file:
   - `FIRECRAWL_API_KEY`: Get your key from [Firecrawl](https://firecrawl.dev). Used for web scraping and screenshots.
   - `TINYFISH_API_KEY`: Get your key from [TinyFish](https://tinyfish.ai). Used for browser agents on gated platforms.
   - `UX_INSPO_INDEX_DIR`: (Optional) Path to your local pattern index (defaults to `./uxindex`).

## Running the Server

Start the FastMCP server using `uv`:
```bash
uv run dia-mcp
```

### Using with Claude Desktop (or other MCP clients)

Add the following configuration to your Claude Desktop MCP settings (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dia-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/dia-mcp",
        "run",
        "dia-mcp"
      ],
      "env": {
        "FIRECRAWL_API_KEY": "fc-...",
        "TINYFISH_API_KEY": "tf-..."
      }
    }
  }
}
```
*(Make sure to match the directory path and replace the API keys with your actual keys.)*

## Development Commands

```bash
# Run type checking (pyright)
uv run pyright src/

# Run the linter (ruff)
uv run ruff check src/

# Run the formatter (ruff)
uv run ruff format src/

# Run tests
uv run pytest
```
