"""
Level 11 — Hoch hinaus

Der Ball liegt unten auf dem Boden.
Der Eimer befindet sich auf einem hohen Pfeiler hoch in der Luft!
Ziel: Den Ball nach oben auf den Pfeiler katapultieren.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_PURPLE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level11(BaseLevel):
    LEVEL_NUMBER = 11
    TITLE = "Hoch hinaus"
    GOAL_DESCRIPTION = "Katapultiere den Ball nach oben auf den Pfeiler!"
    HINT = "Baue eine Wippe und lass ein massives Gewicht auf das andere Ende sausen."
    BG_COLOR = (246, 240, 248)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Durchgehender Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Ball links am Boden
        world.add_ball((350, floor_y - 45), color=COLOR_CORAL)

        # Hoher Pfeiler rechts
        world.add_static_segment((1350, floor_y), (1350, 440), color=COLOR_PURPLE, radius=12)
        world.add_static_segment((1200, 440), (1500, 440), color=(140, 120, 100), radius=6)

        # Eimer auf dem Pfeiler
        world.add_bucket((1350, 440), width=150, height=120, color=COLOR_TEAL)
