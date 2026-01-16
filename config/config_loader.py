import json
from datetime import datetime
from pathlib import Path
import re
from utils.file_helpers import validate_path

def load_config(path: str):
    # Validate config file path
    validate_path(path, must_be_file=True)

    # Load JSON
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Convert dates
    cfg["start_date"] = datetime.strptime(cfg["start_date"], "%Y-%m-%d")
    cfg["end_date"]   = datetime.strptime(cfg["end_date"], "%Y-%m-%d")

    # Compile timestamp regex patterns (if present)
    if "timestamp_patterns" in cfg:
        cfg["timestamp_patterns"] = [
            re.compile(pattern) for pattern in cfg["timestamp_patterns"]
        ]

    # Convert log base path
    if "MainLogsPath" in cfg:
        cfg["MainLogsPath"] = Path(cfg["MainLogsPath"])

    return cfg