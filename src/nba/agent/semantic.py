from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from nba.services.config import ROOT


@lru_cache
def load_semantic_catalog() -> dict:
    path = Path(ROOT) / "configs" / "semantic_catalog.yaml"
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def normalize_term(term: str) -> str:
    return term.strip().lower().replace(" ", "_").replace("-", "_")


def get_definition(term: str) -> dict:
    catalog = load_semantic_catalog()
    key = normalize_term(term)
    value = catalog["terms"].get(key)
    if value is None:
        return {
            "found": False,
            "term": key,
            "catalog_version": catalog["catalog_version"],
        }
    return {
        "found": True,
        "term": key,
        "catalog_version": catalog["catalog_version"],
        **value,
    }
