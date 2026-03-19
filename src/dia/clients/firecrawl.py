"""Firecrawl client — thin wrappers around the SDK."""

from __future__ import annotations

from typing import Any

from firecrawl import Firecrawl

from dia.config import FIRECRAWL_API_KEY

_fc: Firecrawl | None = None


def _client() -> Firecrawl:
    global _fc
    if _fc is None:
        _fc = Firecrawl(api_key=FIRECRAWL_API_KEY)
    return _fc


# ── Primitives ───────────────────────────────────────────────


def search(
    query: str, *, limit: int = 5, formats: list[str] | None = None
) -> list[dict[str, Any]]:
    opts: dict[str, Any] | None = None
    if formats:
        opts = {"formats": formats}
    result = _client().search(query, limit=limit, scrape_options=opts)  # type: ignore[arg-type]
    return result or []  # type: ignore[return-value]


def scrape(
    url: str,
    *,
    formats: list[str] | None = None,
    actions: list[dict[str, Any]] | None = None,
    mobile: bool = False,
) -> Any:
    formats = formats or ["markdown", "screenshot"]
    kwargs: dict[str, Any] = {"formats": formats}
    if actions:
        kwargs["actions"] = actions
    if mobile:
        kwargs["mobile"] = True
    return _client().scrape(url, **kwargs)


def map_urls(url: str) -> list[str]:
    result = _client().map(url)  # type: ignore[return-value]
    if hasattr(result, "urls"):
        return result.urls or []  # type: ignore[return-value]
    return []


def batch_scrape(
    urls: list[str],
    *,
    formats: list[str] | None = None,
    mobile: bool = False,
) -> Any:
    formats = formats or ["screenshot", "markdown"]
    kwargs: dict[str, Any] = {
        "formats": formats,
        "poll_interval": 2,
        "wait_timeout": 120,
    }
    if mobile:
        kwargs["mobile"] = True
    return _client().batch_scrape(urls, **kwargs)


def extract_branding(url: str) -> Any:
    doc = _client().scrape(url, formats=["branding", "screenshot"])
    return doc.branding if hasattr(doc, "branding") else doc
