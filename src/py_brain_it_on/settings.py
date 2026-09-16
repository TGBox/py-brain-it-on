"""
settings.py — Globale Konstanten für py-brain-it-on (Brain it on!).
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
WINDOW_TITLE = "Py Brain it on!"
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FPS = 60

# ---------------------------------------------------------------------------
# Farben  (R, G, B)
# ---------------------------------------------------------------------------
COLOR_BG         = (245, 240, 230)
COLOR_BG_DARK    = (230, 222, 210)
COLOR_PANEL      = (255, 252, 248)

COLOR_CORAL      = (255, 107, 107)
COLOR_CORAL_DARK = (220, 75, 75)
COLOR_TEAL       = (78, 205, 196)
COLOR_TEAL_DARK  = (55, 175, 165)
COLOR_YELLOW     = (255, 220, 80)
COLOR_YELLOW_DARK= (210, 170, 40)
COLOR_PURPLE     = (162, 105, 220)
COLOR_GREEN      = (70, 200, 120)
COLOR_GREEN_DARK = (50, 160, 90)
COLOR_ORANGE     = (255, 160, 50)
COLOR_BLUE       = (80, 150, 240)
COLOR_BLUE_DARK  = (50, 110, 200)

COLOR_TEXT       = (45, 52, 54)
COLOR_TEXT_LIGHT = (120, 115, 110)
COLOR_WHITE      = (255, 255, 255)
COLOR_BLACK      = (0, 0, 0)

COLOR_STAR_FILLED= (255, 210, 40)
COLOR_STAR_EMPTY = (200, 190, 175)

# ---------------------------------------------------------------------------
# Physik
# ---------------------------------------------------------------------------
GRAVITY          = (0, 1200)     # px/s^2 (y zeigt nach unten)
PHYSICS_DAMPING  = 0.98          # Luftreibung (1=keine, 0=viel)
BALL_RADIUS      = 24            # px
BALL_MASS        = 1.0
BALL_ELASTICITY  = 0.45
BALL_FRICTION    = 0.6
WALL_FRICTION    = 0.5
WALL_ELASTICITY  = 0.2
SEGMENT_RADIUS   = 5             # Dicke gezeichneter Linien (Physik)
DRAW_SIMPLIFY_TOLERANCE = 4.0    # Douglas-Peucker-Toleranz in px

# ---------------------------------------------------------------------------
# Spielmechanik
# ---------------------------------------------------------------------------
TOTAL_LEVELS     = 25
MAX_HINTS        = 999           # Unbegrenzte Tipps
# Standard-Sternebewertung nach Strichanzahl (wird von Leveln überschreibbar)
STAR_STROKES     = {3: 1, 2: 3}  # <=1 Strich → 3 Sterne, <=3 → 2 Sterne, sonst 1 Stern

# ---------------------------------------------------------------------------
# Animationszeiten (Sekunden)
# ---------------------------------------------------------------------------
ANIM_FAST   = 0.15
ANIM_MEDIUM = 0.30
ANIM_SLOW   = 0.60

# ---------------------------------------------------------------------------
# Font-Größen (für 1080p FullHD)
# ---------------------------------------------------------------------------
FONT_SIZE_XL = 72
FONT_SIZE_LG = 52
FONT_SIZE_MD = 36
FONT_SIZE_SM = 26
FONT_SIZE_XS = 20
