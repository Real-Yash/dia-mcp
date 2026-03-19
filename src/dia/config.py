import os
from pathlib import Path

TINYFISH_API_KEY: str = os.environ.get("TINYFISH_API_KEY", "")
FIRECRAWL_API_KEY: str = os.environ.get("FIRECRAWL_API_KEY", "")

INDEX_DIR: Path = Path(os.environ.get("UX_INSPO_INDEX_DIR", "./uxindex"))
INDEX_DIR.mkdir(exist_ok=True)

DB_PATH: Path = INDEX_DIR / "ux_inspo.db"
