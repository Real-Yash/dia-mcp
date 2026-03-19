"""Walk a real multi-step UI flow with TinyFish."""

from __future__ import annotations

import json

from dia.clients import tinyfish as tf


async def walk_flow(url: str, flow: str) -> str:
    """
    🔬 Walk through a real UI flow on a live product and document every step.

    Args:
        url: Starting URL (e.g. "notion.so")
        flow: What flow to walk, e.g.
              "the signup/onboarding flow"
              "navigate to settings, find dark mode toggle"
              "open pricing, click Pro, go through checkout"
    """
    goal = (
        f"Walk through this flow: {flow}. "
        f"At each step document what you see. Return as JSON: "
        f'{{"flow_name": "{flow}", "steps": [{{'
        f'"step_number": int, '
        f'"screen_title": "what screen this is", '
        f'"url": "current URL", '
        f'"description": "what the screen shows", '
        f'"key_ui_elements": ["notable UI components"], '
        f'"interaction": "what you clicked/did to advance", '
        f'"design_observations": "what stands out about this screen"'
        f"}}]}}"
    )

    result = await tf.run_agent(url, goal, stealth=True)

    return json.dumps(
        {
            "url": url,
            "flow": flow,
            "walkthrough": result.get("resultJson", result),
            "status": result.get("status", "unknown"),
            "reminder": (
                "This documents HOW a top product solved this UX problem. "
                "Extract PRINCIPLES: step count, progressive disclosure, "
                "info hierarchy per step, friction points, delight moments."
            ),
        },
        indent=2,
    )
