"""
Level 18 — Hängebrücke

Vier schwebende Inseln führen treppenförmig hinab zum Eimer.
Dazwischen klaffen weite Lücken ohne Boden.
Ziel: Verbinde die Inseln zu einer durchgehenden Bahn.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_GREEN, WINDOW_WIDTH, WINDOW_HEIGHT


class Level18(BaseLevel):
    LEVEL_NUMBER = 18
    TITLE = "Hängebrücke"
    GOAL_DESCRIPTION = "Verbinde die schwebenden Inseln zum Ziel-Eimer!"
    HINT = "Zeichne eine durchgehende geschwungene Linie, die über die Pfeiler gleitet."
    BG_COLOR = (240, 246, 244)
    STAR_THRESHOLDS = (1, 3)
    SOLUTION_DESCRIPTION = "Durchgehende Brücke: Ein geschwungener Steg über alle Inseln mit integriertem Brems-Stopper am Eimer."
    SOLUTION_STROKES = [
        [(240, 280), (280, 370), (550, 440), (800, 500), (1050, 560), (1300, 600), (1500, 640), (1630, 660), (1660, 720), (1720, 720), (1740, 500)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Insel 1 mit Ball
        world.add_static_segment((150, 380), (450, 380), color=COLOR_GREEN, radius=8)
        world.add_ball((280, 330), color=COLOR_CORAL)

        # Insel 2
        world.add_static_segment((680, 520), (950, 520), color=COLOR_GREEN, radius=8)

        # Insel 3
        world.add_static_segment((1150, 660), (1420, 660), color=COLOR_GREEN, radius=8)

        # Insel 4 mit Eimer
        world.add_static_segment((1520, 800), (1850, 800), color=COLOR_GREEN, radius=8)
        world.add_bucket((1680, 800), width=150, height=120, color=COLOR_TEAL)

        # Boden weit unten
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)
