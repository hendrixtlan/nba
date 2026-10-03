from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    json_files = sorted((ROOT / "fabric" / "data-contracts").glob("*.json"))
    yaml_files = sorted((ROOT / "fabric" / "pipelines").glob("*.yaml"))
    yaml_files += sorted((ROOT / "azureml").rglob("*.yml"))

    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))
        print(f"valid_json={path.relative_to(ROOT)}")

    for path in yaml_files:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected YAML object: {path}")
        print(f"valid_yaml={path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
