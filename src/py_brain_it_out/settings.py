"""
settings.py — Globale Konstanten, Farben und Design-Tokens für py-brain-it-out.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Verzeichnisse
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent
ASSETS_DIR = ROOT_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# ---------------------------------------------------------------------------
# Fenster
# ---------------------------------------------------------------------------
WINDOW_TITLE = "Py Brain it out!"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# ---------------------------------------------------------------------------
# Farben  (R, G, B)
# ---------------------------------------------------------------------------
# Hintergründe
COLOR_BG = (255, 248, 240)          # warmes Creme
COLOR_BG_DARK = (245, 235, 220)     # etwas dunkler für Panels

# Akzente
COLOR_CORAL = (255, 107, 107)       # Korallrot (Primär)
COLOR_CORAL_DARK = (220, 75, 75)
COLOR_TEAL = (78, 205, 196)         # Türkis (Sekundär)
COLOR_TEAL_DARK = (55, 175, 165)
COLOR_YELLOW = (255, 230, 109)      # Sonnengelb
COLOR_YELLOW_DARK = (230, 200, 70)
COLOR_PURPLE = (162, 105, 220)      # Lila (Akzent)
COLOR_PURPLE_DARK = (130, 80, 185)
COLOR_GREEN = (85, 210, 130)        # Grün (Erfolg)
COLOR_GREEN_DARK = (60, 175, 100)
COLOR_ORANGE = (255, 165, 60)       # Orange

# Neutrals
COLOR_TEXT = (45, 52, 54)           # Dunkelgrau
COLOR_TEXT_LIGHT = (100, 110, 115)  # Hellgrau
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_SHADOW = (0, 0, 0, 60)        # Halbtransparent
COLOR_OVERLAY = (0, 0, 0, 150)      # Dunkles Overlay

# Sterne
COLOR_STAR_FILLED = (255, 220, 50)
COLOR_STAR_EMPTY = (200, 190, 175)

# ---------------------------------------------------------------------------
# Puzzle / Spielmechanik
# ---------------------------------------------------------------------------
MAX_HINTS = 3
TOTAL_LEVELS = 8

# Sternebewertung: (max_fehlversuche, max_hinweise) → Sterne
STAR_THRESHOLDS = {
    3: (1, 0),   # 3 Sterne: ≤1 Fehlversuch, 0 Hinweise
    2: (3, 1),   # 2 Sterne: ≤3 Fehlversuche, ≤1 Hinweis
    1: (999, 999),  # 1 Stern: Rest
}

# ---------------------------------------------------------------------------
# Animationsgeschwindigkeiten (Sekunden)
# ---------------------------------------------------------------------------
ANIM_FAST = 0.15
ANIM_MEDIUM = 0.3
ANIM_SLOW = 0.6

# ---------------------------------------------------------------------------
# Font-Größen
# ---------------------------------------------------------------------------
FONT_SIZE_XL = 48
FONT_SIZE_LG = 36
FONT_SIZE_MD = 28
FONT_SIZE_SM = 22
FONT_SIZE_XS = 16
