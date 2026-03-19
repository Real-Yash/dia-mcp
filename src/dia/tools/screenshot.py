"""Screenshot any live product."""

from __future__ import annotations

import json
from typing import Any

from dia.clients import firecrawl as fc


async def screenshot_live_app(
    url: str,
    mobile: bool = False,
    full_page: bool = False,
    dismiss_popups: bool = True,
) -> str:
    """
    📸 Take a high-quality screenshot of any live app/website.

    Args:
        url: Any URL (stripe.com/pricing, linear.app, etc.)
        mobile: Emulate a mobile viewport
        full_page: Capture the entire scrollable page
        dismiss_popups: Try to dismiss cookie banners / modals first
    """
    fmt = "screenshot@fullPage" if full_page else "screenshot"

    actions: list[dict[str, Any]] | None = None
    if dismiss_popups:
        actions = [
            {"type": "wait", "milliseconds": 2000},
            {
                "type": "click",
                "selector": (
                    "[class*='cookie'] button, [class*='banner'] button, "
                    "[class*='dismiss'], [class*='close'], [aria-label='Close']"
                ),
            },
            {"type": "wait", "milliseconds": 500},
        ]

    result = fc.scrape(url, formats=[fmt, "markdown"], actions=actions, mobile=mobile)

    screenshot = result.get("screenshot")
    meta = result.get("metadata", {}) or {}
    title = meta.get("title", "") if isinstance(meta, dict) else ""

    return json.dumps(
        {
            "url": url,
            "title": title,
            "mobile": mobile,
            "full_page": full_page,
            "screenshot_captured": screenshot is not None,
            "analysis_hint": (
                "Study this screenshot for: visual hierarchy, spacing rhythm, "
                "color usage, typography scale, component patterns, whitespace "
                "strategy. Use observations to INFORM your design, not copy it."
            ),
        }
    )
