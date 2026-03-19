"""Reusable MCP prompts."""

from __future__ import annotations


def inspo_hunt(
    project_description: str,
    specific_screens: str = "",
    style_preference: str = "",
) -> str:
    """Launch a full inspiration hunt for a project."""
    return f"""You are a senior UI/UX researcher. Find inspiration for:

PROJECT: {project_description}
{f"SCREENS NEEDED: {specific_screens}" if specific_screens else ""}
{f"STYLE: {style_preference}" if style_preference else ""}

Execute this plan:

1. **find_inspo** — 2-3 searches from different angles (screen type,
   industry, specific component).

2. **screenshot_live_app** — Top 3-5 real products that solve similar
   problems. Screenshot their actual live UIs.

3. **dig_platform** on Mobbin or Refero — Deep-dive for specific screen
   patterns.

4. **extract_design_dna** — Pick the 2 best references, extract their
   design systems to understand token relationships.

5. **walk_flow** — If the project has a multi-step flow, walk 1-2
   best-in-class examples.

COMPILE AS:

🎨 **Inspiration Board** — Top 8-12 images with 1-2 sentences each on
   WHY they're relevant.

🧠 **Design Principles** — 5-7 principles observed across the best
   references (not "copy X's colors" but "use high-contrast CTAs against
   muted backgrounds for clear hierarchy").

🧬 **Token Patterns** — Typography scales, color relationships, spacing
   rhythms from the best references.

🗺️ **Flow Patterns** — Step-by-step patterns that work best for this
   type of user journey.

⚡ **Recommendations** — 3-5 actionable design directions INSPIRED BY
   (not copied from) the references.

Goal: ELEVATE the designer's understanding, not provide a template."""
