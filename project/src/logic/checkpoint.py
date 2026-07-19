import json
from pathlib import Path
from typing import Dict, Any

def load_checkpoint(path: str | Path) -> Dict[str, Any]:
    """Loads a JSON checkpoint if it exists."""
    cp_path = Path(path)
    if cp_path.exists():
        with open(cp_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_checkpoint(path: str | Path, data: Dict[str, Any]) -> None:
    """Saves data to a JSON checkpoint."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
