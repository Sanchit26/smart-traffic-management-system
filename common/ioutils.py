import json, os, tempfile
from pathlib import Path
from typing import Dict, Any, Optional

def write_json_atomic(path: os.PathLike, data: Dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent)) as tmp:
            json.dump(data, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = tmp.name
        os.replace(tmp_path, path)
    finally:
        if tmp and os.path.exists(tmp.name):
            os.remove(tmp.name)

def read_latest_json(path: os.PathLike) -> Optional[Dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return None
    try:
        if path.suffix == ".jsonl":
            with path.open("r") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
                if not lines:
                    return None
                return json.loads(lines[-1])
        else:
            return json.loads(path.read_text())
    except Exception as e:
        print(f"⚠️ Error reading {path}: {e}")
        return None
