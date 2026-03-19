"""UI/UX Inspo MCP Server — find the best UI/UX inspiration as images, fast."""

from __future__ import annotations

import json

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

from dia.clients import firecrawl as fc
from dia.index.db import init as init_db, save_pattern, search_patterns
from dia.tools.find_inspo import find_inspo
from dia.tools.screenshot import screenshot_live_app
from dia.tools.dig_platform import dig_platform
from dia.tools.compare import compare_uis
from dia.tools.design_dna import extract_design_dna
from dia.tools.walk_flow import walk_flow
from dia.prompts.inspo_hunt import inspo_hunt

# ── Lifespan ──────────────────────────────────────────────────


@lifespan
async def _lifespan(server: FastMCP):
    await init_db()
    yield


# ── Server ────────────────────────────────────────────────────

mcp = FastMCP(
    "UX Inspo Engine 🎨",
    instructions=(
        "You are a UI/UX inspiration engine. You find the best visual "
        "design references from across the web as IMAGES — screenshots "
        "of real shipped products and curated design platforms.\n\n"
        "CARDINAL RULE: Deliver inspiration alongside DESIGN REASONING "
        "(why it works, what pattern it uses, what principle it demonstrates). "
        "NEVER help copy a design. Help the user UNDERSTAND what makes it "
        "great so they create something original informed by the best.\n\n"
        "Always return images. Speed is everything. Hit multiple sources "
        "in parallel when possible."
    ),
    lifespan=_lifespan,
)

# ── Tools ─────────────────────────────────────────────────────

mcp.add_tool(find_inspo)
mcp.add_tool(screenshot_live_app)
mcp.add_tool(dig_platform)
mcp.add_tool(compare_uis)
mcp.add_tool(extract_design_dna)
mcp.add_tool(walk_flow)


@mcp.tool
async def index_pattern(
    url: str,
    app_name: str,
    flow_name: str,
    category: str,
    description: str,
    tags: str = "",
) -> str:
    """
    💾 Save a UI/UX pattern to the local research index.

    category: onboarding | checkout | settings | dashboard | navigation
              | forms | modals | empty-states | error-handling | pricing
    tags: comma-separated, e.g. "dark-mode,mobile,saas,minimalist"
    """
    scraped = fc.scrape(url, formats=["markdown", "screenshot"])
    md = scraped.get("markdown", "") or ""
    ss = scraped.get("screenshot", "") or ""

    pid = await save_pattern(
        {
            "url": url,
            "app_name": app_name,
            "flow_name": flow_name,
            "category": category,
            "description": description,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "markdown": md,
            "screenshot_b64": ss,
        }
    )
    return json.dumps({"indexed": True, "pattern_id": pid, "app_name": app_name})


@mcp.tool
async def search_index(
    query: str = "",
    category: str = "",
    tags: str = "",
    limit: int = 20,
) -> str:
    """🔎 Search the local UI/UX pattern index."""
    results = await search_patterns(
        query=query, category=category, tags=tags, limit=limit
    )
    return json.dumps(results, indent=2)


# ── Prompt ────────────────────────────────────────────────────

mcp.prompt()(inspo_hunt)


# ── Entrypoint ────────────────────────────────────────────────


def main():
    mcp.run()


if __name__ == "__main__":
    main()
