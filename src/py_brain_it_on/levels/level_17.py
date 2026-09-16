"""
Level 17 — Hoch hinaus

Der Ball liegt unten auf dem Boden.
Der Eimer befindet sich auf einem hohen Pfeiler hoch in der Luft!
Ziel: Den Ball nach oben auf den Pfeiler katapultieren.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_PURPLE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level17(BaseLevel):
    LEVEL_NUMBER = 17
    TITLE = "Hoch hinaus"
    GOAL_DESCRIPTION = "Katapultiere den Ball nach oben auf den Pfeiler!"
    HINT = "Baue eine Wippe und lass ein massives Gewicht auf das andere Ende sausen."
    BG_COLOR = (246, 240, 248)
    STAR_THRESHOLDS = (1, 3)
    SOLUTION_DESCRIPTION = "Katapult-Stoß: Ein schweres Gewicht saust auf die Wippe und schleudert den Ball hoch auf den Pfeiler."
    SOLUTION_STROKES = [
        [(410, 300), (480, 300), (480, 370), (410, 370), (410, 300)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Durchgehender Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Wippe links für Katapult
        world.add_static_segment((600, floor_y), (600, floor_y - 70), color=COLOR_PURPLE, radius=8)
        world.add_dynamic_box((600, floor_y - 85), width=520, height=22, mass=4.0, color=(160, 110, 70))
        world.add_ball((780, floor_y - 120), color=COLOR_CORAL)

        # Hoher Pfeiler rechts
        world.add_static_segment((1350, floor_y), (1350, 440), color=COLOR_PURPLE, radius=12)
        world.add_static_segment((1200, 440), (1500, 440), color=(140, 120, 100), radius=6)

        # Eimer auf dem Pfeiler
        world.add_bucket((1350, 440), width=150, height=120, color=COLOR_TEAL)
