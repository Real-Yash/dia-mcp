"""Platform registry — every inspiration source the server knows how to mine."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InspoSource:
    name: str
    url: str
    search_url: str = ""
    needs: str = "firecrawl"  # "firecrawl" | "tinyfish"
    strength: str = ""
    platforms: list[str] = field(default_factory=list)


SOURCES: dict[str, InspoSource] = {
    # ── Tier S ──────────────────────────────────────
    "mobbin": InspoSource(
        name="Mobbin",
        url="https://mobbin.com",
        search_url="https://mobbin.com/browse/{platform}/screens?q={query}",
        needs="tinyfish",
        strength="400k+ real shipped app screenshots — mobile & web",
        platforms=["ios", "android", "web"],
    ),
    "refero": InspoSource(
        name="Refero",
        url="https://refero.design",
        search_url="https://refero.design/search?q={query}",
        needs="tinyfish",
        strength="112k+ screens tagged by component, flow, and pattern",
    ),
    "dribbble": InspoSource(
        name="Dribbble",
        url="https://dribbble.com",
        search_url="https://dribbble.com/search/{query}",
        needs="firecrawl",
        strength="Polished visual shots, color/style trends",
    ),
    # ── Tier A ──────────────────────────────────────
    "godly": InspoSource(
        name="Godly",
        url="https://godly.website",
        needs="tinyfish",
        strength="Motion design & cutting-edge web design",
    ),
    "screenlane": InspoSource(
        name="Screenlane",
        url="https://screenlane.com",
        search_url="https://screenlane.com/?q={query}",
        needs="firecrawl",
        strength="Mobile + web UI, filterable by category",
    ),
    "collectui": InspoSource(
        name="Collect UI",
        url="https://collectui.com",
        needs="firecrawl",
        strength="Best Dribbble shots sorted by component type",
    ),
    "behance": InspoSource(
        name="Behance",
        url="https://behance.net",
        needs="firecrawl",
        strength="Full case studies with design rationale",
    ),
    # ── Tier B ──────────────────────────────────────
    "landingfolio": InspoSource(
        name="Landingfolio",
        url="https://landingfolio.com",
        needs="firecrawl",
        strength="SaaS landing pages + component gallery",
    ),
    "designvault": InspoSource(
        name="Design Vault",
        url="https://designvault.io",
        needs="firecrawl",
        strength="Breakdowns of WHY designs work",
    ),
}


def pick_sources(query: str, ui_type: str = "any") -> list[str]:
    """Heuristically pick the best 2-3 sources for a query."""
    q = query.lower()

    if ui_type in ("mobile", "ios", "android") or any(
        w in q for w in ["mobile", "ios", "android", "app screen", "bottom sheet"]
    ):
        return ["mobbin", "screenlane", "collectui"]

    if any(w in q for w in ["landing", "pricing", "hero", "saas", "homepage"]):
        return ["landingfolio", "godly", "dribbble"]

    if any(
        w in q
        for w in [
            "login",
            "signup",
            "404",
            "empty state",
            "settings",
            "onboarding",
            "checkout",
            "form",
            "modal",
            "toast",
        ]
    ):
        return ["mobbin", "collectui", "screenlane"]

    if any(w in q for w in ["dashboard", "analytics", "admin", "table", "chart"]):
        return ["refero", "dribbble", "behance"]

    if any(w in q for w in ["design system", "why", "breakdown", "case study"]):
        return ["designvault", "behance"]

    return ["dribbble", "mobbin", "godly"]
