"""
Level 21 — Schwerelos

Eine schwere Holzkiste steht auf dem Boden.
Ziel: Hebe die Kiste mit Hebelkraft oder Gegengewichten hoch in die Luft!
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import WINDOW_WIDTH, WINDOW_HEIGHT


class Level21(BaseLevel):
    LEVEL_NUMBER = 21
    TITLE = "Schwerelos"
    GOAL_DESCRIPTION = "Hebe die Holzkiste deutlich in die Höhe!"
    HINT = "Zeichne einen langen Hebel unter die Kiste und lass ein schweres Gegengewicht auf das freie Ende fallen."
    BG_COLOR = (246, 243, 238)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Drehpunkt in der Nähe der Kiste
        world.add_static_segment((850, floor_y), (850, floor_y - 80), color=(120, 100, 80), radius=8)

        # Schwere Kiste (y = floor_y - 60)
        world.add_dynamic_box((980, floor_y - 60), width=150, height=120, mass=6.0, color=(170, 105, 55))

    def check_victory(self, world: PhysicsWorld, dt: float = 0.0) -> bool:
        if not world.dynamic_boxes:
            return False
        box = world.dynamic_boxes[0]
        return box.is_lifted
