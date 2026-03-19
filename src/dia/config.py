import os
from pathlib import Path

# Automatically load .env if present (so `fastmcp run` works without souring)
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        if _line.strip() and not _line.startswith("#"):
            _k, _, _v = _line.partition("=")
            if _k.strip() not in os.environ:
                os.environ[_k.strip()] = _v.strip()

TINYFISH_API_KEY: str = os.environ.get("TINYFISH_API_KEY", "")
FIRECRAWL_API_KEY: str = os.environ.get("FIRECRAWL_API_KEY", "")

INDEX_DIR: Path = Path(os.environ.get("UX_INSPO_INDEX_DIR", "./uxindex"))


def ensure_index_dir():
    """Lazily create the index directory."""
    if not INDEX_DIR.exists():
        INDEX_DIR.mkdir(parents=True, exist_ok=True)


DB_PATH: Path = INDEX_DIR / "ux_inspo.db"
