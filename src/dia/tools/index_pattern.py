"""Tool — save a UI/UX pattern to the local research index."""

from __future__ import annotations

import json

from dia.clients import firecrawl as fc
from dia.index.db import save_pattern


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
