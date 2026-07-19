import os
from pathlib import Path

def ensure_output_dir(path: str = "output") -> Path:
    """Ensures output directory exists."""
    out_dir = Path(path)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir
