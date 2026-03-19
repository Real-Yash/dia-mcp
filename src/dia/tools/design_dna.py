"""Extract visual design tokens from any live site."""

from __future__ import annotations

import json

from dia.clients import firecrawl as fc


async def extract_design_dna(url: str) -> str:
    """
    🧬 Extract the design system of any live website.

    Returns: color palette, typography, spacing, button styles.
    Understand the RELATIONSHIPS between tokens — not to copy values.
    """
    result = fc.scrape(url, formats=["branding", "screenshot"])

    branding = getattr(result, "branding", None) or (
        result.get("branding") if isinstance(result, dict) else None
    )
    screenshot = getattr(result, "screenshot", None) or (
        result.get("screenshot") if isinstance(result, dict) else None
    )

    return json.dumps(
        {
            "url": url,
            "design_dna": branding,
            "has_screenshot": screenshot is not None,
            "interpretation_guide": (
                "Study RELATIONSHIPS: heading-to-body size ratio, "
                "primary-to-accent color contrast, spacing scale. "
                "These proportional relationships make a system cohesive — "
                "use them as inspiration for YOUR OWN token system."
            ),
        },
        indent=2,
    )
