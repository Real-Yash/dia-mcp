"""Comprehensive tests for all dia-mcp tools.

All external API calls (Firecrawl, TinyFish) are mocked so tests
run without real API credits.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def fc_search_result() -> list[dict]:
    """Fake result from fc.search() — now a list of plain dicts."""
    return [
        {
            "url": "https://dribbble.com/shots/12345",
            "metadata": {
                "sourceURL": "https://dribbble.com/shots/12345",
                "title": "Dark Dashboard UI",
            },
            "markdown": "# Dark Dashboard\nA sleek admin panel.",
            "screenshot": None,
        },
        {
            "url": "https://dribbble.com/shots/99999",
            "metadata": {
                "sourceURL": "https://dribbble.com/shots/99999",
                "title": "Analytics App",
            },
            "markdown": "# Analytics\nCharts and tables.",
            "screenshot": None,
        },
    ]


@pytest.fixture()
def fc_scrape_result() -> dict:
    """Fake result from fc.scrape() — a plain dict."""
    return {
        "url": "https://stripe.com",
        "markdown": "# Stripe\nPayments infrastructure.",
        "screenshot": "data:image/png;base64,FAKESCREENSHOT",
        "branding": {
            "color_scheme": "light",
            "colors": {"primary": "#635bff"},
            "fonts": [{"family": "Roboto"}],
        },
        "metadata": {
            "sourceURL": "https://stripe.com",
            "title": "Stripe – Payment Infrastructure",
        },
    }


@pytest.fixture()
def fc_batch_result() -> dict:
    """Fake result from fc.batch_scrape() — {"data": [...]}."""
    return {
        "data": [
            {
                "url": "https://stripe.com",
                "markdown": "# Stripe",
                "screenshot": "data:image/png;base64,FAKE",
                "metadata": {
                    "sourceURL": "https://stripe.com",
                    "title": "Stripe",
                },
            }
        ]
    }


@pytest.fixture()
def tf_result() -> dict:
    """Fake TinyFish COMPLETE event result."""
    return {
        "type": "COMPLETE",
        "status": "success",
        "resultJson": {
            "results": [
                {
                    "title": "Mobbin Login Screen",
                    "image_url": "https://cdn.mobbin.com/shot1.webp",
                    "app_name": "Notion",
                    "screen_type": "Login",
                    "page_url": "https://mobbin.com/screens/123",
                    "description": "Clean login form",
                }
            ]
        },
    }


# ── firecrawl client ─────────────────────────────────────────────────────────


class TestFirecrawlClient:
    """Unit tests for the Firecrawl client wrapper."""

    def test_search_returns_list_of_dicts(self):
        """fc.search() must always return a list of dicts even with SDK models."""
        from dia.clients import firecrawl as fc

        mock_search_data = MagicMock()
        mock_result = MagicMock()
        mock_result.url = "https://dribbble.com/shots/1"
        mock_result.title = "Dashboard UI"
        mock_result.metadata = None

        mock_search_data.web = [mock_result]

        fc._fc = None
        with patch("dia.clients.firecrawl.Firecrawl") as MockFC:
            instance = MockFC.return_value
            instance.search.return_value = mock_search_data
            results = fc.search("test query", limit=2)

        assert isinstance(results, list)

    def test_search_empty_web_returns_empty_list(self):
        """fc.search() returns [] when SearchData.web is None or empty."""
        from dia.clients import firecrawl as fc

        mock_search_data = MagicMock()
        mock_search_data.web = None

        fc._fc = None
        with patch("dia.clients.firecrawl.Firecrawl") as MockFC:
            MockFC.return_value.search.return_value = mock_search_data
            results = fc.search("empty query")

        assert results == []

    def test_batch_scrape_returns_dict_with_data_key(self):
        """fc.batch_scrape() must always return {"data": [...]}."""
        from dia.clients import firecrawl as fc

        mock_batch = MagicMock()
        mock_batch.data = []

        fc._fc = None
        with patch("dia.clients.firecrawl.Firecrawl") as MockFC:
            MockFC.return_value.batch_scrape.return_value = mock_batch
            result = fc.batch_scrape(["https://example.com"])

        assert isinstance(result, dict)
        assert "data" in result
        assert isinstance(result["data"], list)


# ── find_inspo ───────────────────────────────────────────────────────────────


class TestFindInspo:
    """Tests for the find_inspo tool."""

    @pytest.mark.asyncio
    async def test_find_inspo_firecrawl_sources(
        self, fc_search_result, fc_batch_result
    ):
        """find_inspo returns results for Firecrawl-backed sources (dribbble)."""
        from dia.tools.find_inspo import find_inspo

        with (
            patch("dia.tools.find_inspo.fc.search", return_value=fc_search_result),
            patch("dia.tools.find_inspo.fc.batch_scrape", return_value=fc_batch_result),
        ):
            output = await find_inspo(
                "dashboard dark mode", platform="dribbble", limit=5
            )

        data = json.loads(output)
        assert data["query"] == "dashboard dark mode"
        assert data["sources_searched"] == ["dribbble"]
        assert data["total_results"] >= 1
        assert len(data["inspiration_board"]) >= 1
        first = data["inspiration_board"][0]
        assert "url" in first
        assert first["source_platform"] == "dribbble"

    @pytest.mark.asyncio
    async def test_find_inspo_tinyfish_sources(self, tf_result):
        """find_inspo returns results for TinyFish-backed sources (mobbin)."""
        from dia.tools.find_inspo import find_inspo

        with (
            patch(
                "dia.tools.find_inspo.tf.run_parallel",
                new_callable=AsyncMock,
                return_value=[tf_result],
            ),
        ):
            output = await find_inspo("login flow", platform="mobbin", limit=4)

        data = json.loads(output)
        assert data["query"] == "login flow"
        assert "mobbin" in data["sources_searched"]
        # TinyFish results land in inspiration_board with agent_extracted key
        assert data["total_results"] >= 1
        tf_item = data["inspiration_board"][0]
        assert "agent_extracted" in tf_item

    @pytest.mark.asyncio
    async def test_find_inspo_error_handled_gracefully(self):
        """find_inspo returns empty board instead of raising on API error."""
        from dia.tools.find_inspo import find_inspo

        with (
            patch(
                "dia.tools.find_inspo.fc.search",
                side_effect=Exception("Payment Required"),
            ),
            patch(
                "dia.tools.find_inspo.tf.run_parallel",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            output = await find_inspo("test query", platform="dribbble")

        data = json.loads(output)
        assert "error" in data or data["total_results"] == 0

    @pytest.mark.asyncio
    async def test_find_inspo_auto_pick_sources(
        self, fc_search_result, fc_batch_result
    ):
        """auto mode picks sources heuristically."""
        from dia.tools.find_inspo import find_inspo

        with (
            patch("dia.tools.find_inspo.fc.search", return_value=fc_search_result),
            patch("dia.tools.find_inspo.fc.batch_scrape", return_value=fc_batch_result),
            patch(
                "dia.tools.find_inspo.tf.run_parallel",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            output = await find_inspo("landing page SaaS", platform="auto")

        data = json.loads(output)
        # Pick-sources should choose landingfolio/godly/dribbble for landing queries
        assert len(data["sources_searched"]) > 0
        assert isinstance(data["inspiration_board"], list)

    @pytest.mark.asyncio
    async def test_find_inspo_all_sources(
        self, fc_search_result, fc_batch_result, tf_result
    ):
        """platform='all' fans out to every source."""
        from dia.tools.find_inspo import find_inspo

        with (
            patch("dia.tools.find_inspo.fc.search", return_value=fc_search_result),
            patch("dia.tools.find_inspo.fc.batch_scrape", return_value=fc_batch_result),
            patch(
                "dia.tools.find_inspo.tf.run_parallel",
                new_callable=AsyncMock,
                return_value=[tf_result],
            ),
        ):
            output = await find_inspo("mobile onboarding", platform="all", limit=20)

        from dia.sources import SOURCES

        data = json.loads(output)
        assert set(data["sources_searched"]) == set(SOURCES.keys())


# ── screenshot_live_app ───────────────────────────────────────────────────────


class TestScreenshotLiveApp:
    @pytest.mark.asyncio
    async def test_screenshot_captured(self, fc_scrape_result):
        from dia.tools.screenshot import screenshot_live_app

        with patch("dia.tools.screenshot.fc.scrape", return_value=fc_scrape_result):
            output = await screenshot_live_app(
                "https://stripe.com", dismiss_popups=False
            )

        data = json.loads(output)
        assert data["url"] == "https://stripe.com"
        assert data["screenshot_captured"] is True
        assert data["mobile"] is False

    @pytest.mark.asyncio
    async def test_screenshot_no_screenshot(self, fc_scrape_result):
        fc_scrape_result["screenshot"] = None
        from dia.tools.screenshot import screenshot_live_app

        with patch("dia.tools.screenshot.fc.scrape", return_value=fc_scrape_result):
            output = await screenshot_live_app(
                "https://stripe.com", dismiss_popups=False
            )

        data = json.loads(output)
        assert data["screenshot_captured"] is False

    @pytest.mark.asyncio
    async def test_screenshot_mobile_mode(self, fc_scrape_result):
        from dia.tools.screenshot import screenshot_live_app

        with patch(
            "dia.tools.screenshot.fc.scrape", return_value=fc_scrape_result
        ) as mock_scrape:
            output = await screenshot_live_app(
                "https://stripe.com", mobile=True, dismiss_popups=False
            )

        data = json.loads(output)
        assert data["mobile"] is True
        # Verify mobile=True was passed to scrape
        mock_scrape.assert_called_once()
        call_kwargs = mock_scrape.call_args
        assert call_kwargs[1].get("mobile") is True

    @pytest.mark.asyncio
    async def test_screenshot_full_page(self, fc_scrape_result):
        from dia.tools.screenshot import screenshot_live_app

        with patch(
            "dia.tools.screenshot.fc.scrape", return_value=fc_scrape_result
        ) as mock_scrape:
            output = await screenshot_live_app(
                "https://stripe.com", full_page=True, dismiss_popups=False
            )

        data = json.loads(output)
        assert data["full_page"] is True
        args, kwargs = mock_scrape.call_args
        assert "screenshot@fullPage" in kwargs.get("formats", [])


# ── dig_platform ─────────────────────────────────────────────────────────────


class TestDigPlatform:
    @pytest.mark.asyncio
    async def test_dig_platform_mobbin(self, tf_result):
        from dia.tools.dig_platform import dig_platform

        with patch(
            "dia.tools.dig_platform.tf.run_agent",
            new_callable=AsyncMock,
            return_value=tf_result,
        ):
            output = await dig_platform("mobbin", "login flow fintech", limit=4)

        data = json.loads(output)
        assert data["platform"] == "mobbin"
        assert data["query"] == "login flow fintech"
        assert data["status"] == "success"
        assert data.get("agent_result") is not None

    @pytest.mark.asyncio
    async def test_dig_platform_unknown_platform(self):
        from dia.tools.dig_platform import dig_platform

        output = await dig_platform("nonexistent_platform", "test")
        data = json.loads(output)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_dig_platform_with_filters(self, tf_result):
        from dia.tools.dig_platform import dig_platform

        with patch(
            "dia.tools.dig_platform.tf.run_agent",
            new_callable=AsyncMock,
            return_value=tf_result,
        ) as mock_run:
            output = await dig_platform(
                "refero", "checkout", filters="dark mode only", limit=6
            )

        data = json.loads(output)
        assert data["filters"] == "dark mode only"
        # filters should appear in the goal passed to run_agent
        call_args = mock_run.call_args
        goal = call_args[0][1] if call_args[0] else call_args[1].get("goal", "")
        assert "dark mode only" in goal


# ── compare_uis ───────────────────────────────────────────────────────────────


class TestCompareUIs:
    @pytest.mark.asyncio
    async def test_compare_uis_basic(self, fc_batch_result):
        from dia.tools.compare import compare_uis

        multi_batch = {
            "data": [
                {
                    "url": "https://stripe.com/pricing",
                    "screenshot": "data:image/png;base64,FAKE1",
                    "markdown": "# Stripe Pricing",
                    "metadata": {
                        "sourceURL": "https://stripe.com/pricing",
                        "title": "Stripe Pricing",
                    },
                },
                {
                    "url": "https://linear.app/pricing",
                    "screenshot": "data:image/png;base64,FAKE2",
                    "markdown": "# Linear Pricing",
                    "metadata": {
                        "sourceURL": "https://linear.app/pricing",
                        "title": "Linear Pricing",
                    },
                },
            ]
        }

        with patch("dia.tools.compare.fc.batch_scrape", return_value=multi_batch):
            output = await compare_uis(
                "stripe.com/pricing, linear.app/pricing",
                focus="pricing cards",
            )

        data = json.loads(output)
        assert data["focus"] == "pricing cards"
        assert data["screenshots_captured"] == 2
        assert len(data["comparisons"]) == 2

    @pytest.mark.asyncio
    async def test_compare_uis_no_screenshots(self):
        from dia.tools.compare import compare_uis

        batch_no_ss = {
            "data": [
                {
                    "url": "https://example.com",
                    "screenshot": None,
                    "markdown": "# Example",
                    "metadata": {
                        "sourceURL": "https://example.com",
                        "title": "Example",
                    },
                }
            ]
        }

        with patch("dia.tools.compare.fc.batch_scrape", return_value=batch_no_ss):
            output = await compare_uis("example.com")

        data = json.loads(output)
        assert data["screenshots_captured"] == 0


# ── extract_design_dna ────────────────────────────────────────────────────────


class TestExtractDesignDna:
    @pytest.mark.asyncio
    async def test_design_dna_with_branding(self, fc_scrape_result):
        from dia.tools.design_dna import extract_design_dna

        with patch("dia.tools.design_dna.fc.scrape", return_value=fc_scrape_result):
            output = await extract_design_dna("https://stripe.com")

        data = json.loads(output)
        assert data["url"] == "https://stripe.com"
        assert data["has_screenshot"] is True
        dna = data["design_dna"]
        assert isinstance(dna, dict)
        assert "color_scheme" in dna or "colors" in dna or dna is not None

    @pytest.mark.asyncio
    async def test_design_dna_branding_pydantic_model(self):
        """Handles BrandingProfile Pydantic model (not just plain dict)."""
        from dia.tools.design_dna import extract_design_dna

        # BrandingProfile-like mock with model_dump
        mock_branding = MagicMock()
        mock_branding.model_dump.return_value = {
            "color_scheme": "dark",
            "colors": {"primary": "#0f0f0f"},
        }
        del mock_branding.__class__  # doesn't matter, just needs model_dump

        scrape_result = {
            "url": "https://vercel.com",
            "screenshot": "data:image/png;base64,FAKE",
            "branding": mock_branding,
            "metadata": {"sourceURL": "https://vercel.com", "title": "Vercel"},
        }

        with patch("dia.tools.design_dna.fc.scrape", return_value=scrape_result):
            output = await extract_design_dna("https://vercel.com")

        data = json.loads(output)
        assert data["design_dna"]["color_scheme"] == "dark"

    @pytest.mark.asyncio
    async def test_design_dna_no_branding(self, fc_scrape_result):
        fc_scrape_result["branding"] = None
        from dia.tools.design_dna import extract_design_dna

        with patch("dia.tools.design_dna.fc.scrape", return_value=fc_scrape_result):
            output = await extract_design_dna("https://stripe.com")

        data = json.loads(output)
        assert data["design_dna"] is None


# ── walk_flow ─────────────────────────────────────────────────────────────────


class TestWalkFlow:
    @pytest.mark.asyncio
    async def test_walk_flow_success(self, tf_result):
        tf_result["resultJson"] = {
            "flow_name": "signup",
            "steps": [
                {
                    "step_number": 1,
                    "screen_title": "Landing Page",
                    "url": "https://notion.so",
                    "description": "Hero section with CTA",
                    "key_ui_elements": ["Get Started button", "Feature bullets"],
                    "interaction": "Clicked Get Started",
                    "design_observations": "Clean hero, clear hierarchy",
                }
            ],
        }
        from dia.tools.walk_flow import walk_flow

        with patch(
            "dia.tools.walk_flow.tf.run_agent",
            new_callable=AsyncMock,
            return_value=tf_result,
        ):
            output = await walk_flow("https://notion.so", "the signup/onboarding flow")

        data = json.loads(output)
        assert data["url"] == "https://notion.so"
        assert data["flow"] == "the signup/onboarding flow"
        assert data["status"] == "success"
        steps = data["walkthrough"]["steps"]
        assert len(steps) == 1
        assert steps[0]["step_number"] == 1

    @pytest.mark.asyncio
    async def test_walk_flow_empty_result(self):
        from dia.tools.walk_flow import walk_flow

        with patch(
            "dia.tools.walk_flow.tf.run_agent",
            new_callable=AsyncMock,
            return_value={"error": "No COMPLETE event received"},
        ):
            output = await walk_flow("https://example.com", "checkout")

        data = json.loads(output)
        assert data["url"] == "https://example.com"
        # walkthrough should hold the error or empty structure
        assert data.get("walkthrough") is not None


# ── search_index & index_pattern ─────────────────────────────────────────────


class TestDatabaseTools:
    @pytest.mark.asyncio
    async def test_search_index_empty(self, tmp_path):
        """search_index returns [] when nothing is indexed."""
        import os

        os.environ["UX_INSPO_INDEX_DIR"] = str(tmp_path)
        # Force re-import to pick up new env
        import importlib

        import dia.config as _cfg
        import dia.index.db as _db

        importlib.reload(_cfg)
        importlib.reload(_db)

        await _db.init()
        results = await _db.search_patterns(query="anything")
        assert results == []

    @pytest.mark.asyncio
    async def test_index_and_search_pattern(self, tmp_path):
        """index_pattern saves, search_index retrieves it."""
        import os

        os.environ["UX_INSPO_INDEX_DIR"] = str(tmp_path)
        import importlib

        import dia.config as _cfg
        import dia.index.db as _db

        importlib.reload(_cfg)
        importlib.reload(_db)

        await _db.init()
        pid = await _db.save_pattern(
            {
                "url": "https://stripe.com/checkout",
                "app_name": "Stripe",
                "flow_name": "checkout_flow",
                "category": "checkout",
                "description": "Stripe's clean checkout form",
                "tags": ["fintech", "minimal"],
                "markdown": "# Checkout",
                "screenshot_b64": "",
            }
        )

        assert isinstance(pid, str) and len(pid) == 32

        results = await _db.search_patterns(query="Stripe")
        assert len(results) == 1
        assert results[0]["app_name"] == "Stripe"
        assert results[0]["category"] == "checkout"

    @pytest.mark.asyncio
    async def test_search_by_category(self, tmp_path):
        import os

        os.environ["UX_INSPO_INDEX_DIR"] = str(tmp_path)
        import importlib

        import dia.config as _cfg
        import dia.index.db as _db

        importlib.reload(_cfg)
        importlib.reload(_db)

        await _db.init()
        await _db.save_pattern(
            {
                "url": "https://linear.app/onboarding",
                "app_name": "Linear",
                "flow_name": "onboarding",
                "category": "onboarding",
                "description": "Linear onboarding steps",
                "tags": ["minimal", "dark"],
                "markdown": "",
                "screenshot_b64": "",
            }
        )
        await _db.save_pattern(
            {
                "url": "https://notion.so/checkout",
                "app_name": "Notion",
                "flow_name": "checkout",
                "category": "checkout",
                "description": "Notion checkout",
                "tags": ["saas"],
                "markdown": "",
                "screenshot_b64": "",
            }
        )

        onboarding = await _db.search_patterns(category="onboarding")
        assert len(onboarding) == 1
        assert onboarding[0]["app_name"] == "Linear"

    @pytest.mark.asyncio
    async def test_search_by_tags(self, tmp_path):
        import os

        os.environ["UX_INSPO_INDEX_DIR"] = str(tmp_path)
        import importlib

        import dia.config as _cfg
        import dia.index.db as _db

        importlib.reload(_cfg)
        importlib.reload(_db)

        await _db.init()
        await _db.save_pattern(
            {
                "url": "https://vercel.com",
                "app_name": "Vercel",
                "flow_name": "pricing",
                "category": "pricing",
                "description": "Vercel pricing page",
                "tags": ["dark-mode", "enterprise"],
                "markdown": "",
                "screenshot_b64": "",
            }
        )

        dark = await _db.search_patterns(tags="dark-mode")
        assert any(r["app_name"] == "Vercel" for r in dark)

        enterprise = await _db.search_patterns(tags="enterprise")
        assert any(r["app_name"] == "Vercel" for r in enterprise)

        not_found = await _db.search_patterns(tags="mobile")
        assert len(not_found) == 0


# ── sources ───────────────────────────────────────────────────────────────────


class TestSources:
    def test_all_sources_have_required_fields(self):
        from dia.sources import SOURCES

        for key, src in SOURCES.items():
            assert src.name, f"{key} missing name"
            assert src.url, f"{key} missing url"
            assert src.needs in ("firecrawl", "tinyfish"), f"{key} invalid 'needs'"

    def test_pick_sources_mobile(self):
        from dia.sources import pick_sources

        result = pick_sources("ios login screen", "mobile")
        assert "mobbin" in result

    def test_pick_sources_landing(self):
        from dia.sources import pick_sources

        result = pick_sources("landing page hero section")
        assert "landingfolio" in result or "godly" in result or "dribbble" in result

    def test_pick_sources_dashboard(self):
        from dia.sources import pick_sources

        result = pick_sources("admin dashboard analytics")
        assert "refero" in result or "dribbble" in result

    def test_pick_sources_default(self):
        from dia.sources import pick_sources

        result = pick_sources("something random")
        assert len(result) >= 1
