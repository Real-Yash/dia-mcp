"""Primary tool — fan-out search across inspiration platforms."""

from __future__ import annotations

import asyncio
import json

from fastmcp import Context

from dia.clients import firecrawl as fc
from dia.clients import tinyfish as tf
from dia.sources import SOURCES, pick_sources

DESIGN_GUIDANCE = (
    "REMEMBER: These references are for UNDERSTANDING design patterns "
    "and principles. Analyze WHY each design works — the visual hierarchy, "
    "spacing, color relationships, interaction patterns — then create "
    "something original that's informed by these insights."
)


async def find_inspo(
    query: str,
    platform: str = "auto",
    ui_type: str = "any",
    limit: int = 12,
    ctx: Context | None = None,
) -> str:
    """
    🎨 Find the best UI/UX inspiration images for any design need.

    Searches multiple curated platforms in parallel and returns
    screenshot images with design analysis.

    Args:
        query: e.g. "onboarding flow", "dark mode dashboard",
               "pricing page SaaS", "mobile navigation bottom sheet"
        platform: "auto" | "mobbin" | "dribbble" | "refero" | "godly"
                  | "screenlane" | "collectui" | "behance" | "all"
        ui_type: "web" | "mobile" | "ios" | "android" | "any"
        limit: target number of results (default 12)
    """
    if platform == "auto":
        source_keys = pick_sources(query, ui_type)
    elif platform == "all":
        source_keys = list(SOURCES.keys())
    else:
        source_keys = [platform]

    if ctx:
        await ctx.report_progress(
            0, 3
        )  # ── Fan out ────────────────────────────────────────────
    fc_tasks: list[dict] = []
    tf_tasks: list[dict] = []
    per_source = max(limit // len(source_keys), 2)

    for key in source_keys:
        src = SOURCES.get(key)
        if src is None:
            continue
        if src.needs == "firecrawl":
            fc_tasks.append(
                {
                    "source": key,
                    "query": f"{query} UI UX design site:{src.url.replace('https://', '')}",
                    "limit": per_source,
                }
            )
        else:
            search_url = src.search_url or src.url
            if "{query}" in search_url:
                search_url = search_url.format(
                    query=query.replace(" ", "+"),
                    platform=ui_type if ui_type != "any" else "web",
                )
            tf_tasks.append(
                {
                    "url": search_url,
                    "goal": (
                        f"Search for '{query}' UI/UX designs. "
                        f"Find the top {per_source} most relevant results. "
                        f"For each, extract as JSON: "
                        f'{{"results": [{{"title": str, "image_url": str, '
                        f'"app_name": str, "screen_type": str, '
                        f'"page_url": str, "description": str}}]}}'
                    ),
                    "stealth": key in ("mobbin", "refero"),
                }
            )

    fc_results: list[dict] = []
    tf_results: list[dict] = []

    async def _fc_search():
        for task in fc_tasks:
            try:
                res = fc.search(
                    task["query"],
                    limit=task["limit"],
                    formats=["markdown", "screenshot", "links"],
                )
                fc_results.append({"source": task["source"], "results": res})
            except Exception as e:
                fc_results.append({"source": task["source"], "error": str(e)})

    async def _tf_search():
        nonlocal tf_results
        raw = await tf.run_parallel(tf_tasks)
        for i, r in enumerate(raw):
            tf_results.append({"source": tf_tasks[i]["url"], "data": r})

    await asyncio.gather(_fc_search(), _tf_search())

    if ctx:
        await ctx.report_progress(1, 3)

    # ── Collect URLs for batch screenshot ──────────────────
    screenshot_urls: list[str] = []
    for fc_res in fc_results:
        for r in fc_res.get("results") or []:
            url = r.get("url") or r.get("metadata", {}).get("url", "")
            if url:
                screenshot_urls.append(url)

    screenshots: dict[str, bool] = {}
    if screenshot_urls:
        try:
            batch = fc.batch_scrape(screenshot_urls[:limit])
            items = batch.get("data", []) if isinstance(batch, dict) else batch
            for doc in items:
                d = doc if isinstance(doc, dict) else doc.__dict__
                u = d.get("metadata", {}).get("sourceURL", "")
                screenshots[u] = d.get("screenshot") is not None
        except Exception:
            pass

    if ctx:
        await ctx.report_progress(2, 3)
    # ── Compile board ──────────────────────────────────────
    board: list[dict] = []
    seen: set[str] = set()

    for fc_res in fc_results:
        for r in fc_res.get("results") or []:
            url = r.get("url") or r.get("metadata", {}).get("url", "")
            if url in seen:
                continue
            seen.add(url)
            board.append(
                {
                    "source_platform": fc_res["source"],
                    "url": url,
                    "title": r.get("metadata", {}).get("title", ""),
                    "preview": (r.get("markdown") or "")[:300],
                    "has_screenshot": screenshots.get(url, False),
                }
            )

    for tf_res in tf_results:
        data = tf_res.get("data", {})
        rj = data.get("resultJson") if isinstance(data, dict) else None
        if rj:
            board.append(
                {
                    "source_platform": tf_res["source"],
                    "agent_extracted": rj,
                }
            )

    if ctx:
        await ctx.report_progress(3, 3)

    return json.dumps(
        {
            "query": query,
            "sources_searched": source_keys,
            "total_results": len(board),
            "inspiration_board": board[:limit],
            "design_guidance": DESIGN_GUIDANCE,
        },
        indent=2,
    )
