"""
save_manager.py — JSON-basierte lokale Fortschrittsspeicherung.
"""
from __future__ import annotations

import json
from pathlib import Path

from .settings import TOTAL_LEVELS

# Speicherort: ~/.py-brain-it-on/save.json
_SAVE_DIR = Path.home() / ".py-brain-it-on"
_SAVE_FILE = _SAVE_DIR / "save.json"

_DEFAULT_SAVE: dict = {
    "levels": {str(i): {"stars": 0, "solved": False} for i in range(1, TOTAL_LEVELS + 1)},
    "hints_used_total": 0,
}


def _ensure_dir() -> None:
    _SAVE_DIR.mkdir(parents=True, exist_ok=True)


def load() -> dict:
    """Lädt den Spielfortschritt. Gibt Standardwerte zurück, wenn keine Datei existiert."""
    _ensure_dir()
    if not _SAVE_FILE.exists():
        return _deep_copy(_DEFAULT_SAVE)

    try:
        with _SAVE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # Fehlende Level auffüllen
        for i in range(1, TOTAL_LEVELS + 1):
            key = str(i)
            if key not in data.get("levels", {}):
                data.setdefault("levels", {})[key] = {"stars": 0, "solved": False}
        data.setdefault("hints_used_total", 0)
        return data
    except (json.JSONDecodeError, KeyError, TypeError):
        return _deep_copy(_DEFAULT_SAVE)


def save(data: dict) -> None:
    """Speichert den Spielfortschritt."""
    _ensure_dir()
    with _SAVE_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_level_result(data: dict, level: int, stars: int) -> dict:
    """
    Aktualisiert das Ergebnis eines Levels (nur wenn besser als vorher).
    Gibt den aktualisierten Save-Data-Dict zurück.
    """
    key = str(level)
    current = data["levels"].get(key, {"stars": 0, "solved": False})
    if stars > current.get("stars", 0):
        data["levels"][key] = {"stars": stars, "solved": True}
    elif not current.get("solved", False):
        data["levels"][key] = {"stars": stars, "solved": True}
    save(data)
    return data


def _deep_copy(d: dict) -> dict:
    return json.loads(json.dumps(d))
