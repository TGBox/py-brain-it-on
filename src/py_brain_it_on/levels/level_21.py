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
    SOLUTION_DESCRIPTION = "Ein schwerer fallender Block schlägt auf das linke Ende des Hebels und katapultiert die Holzkiste in die Höhe."
    SOLUTION_STROKES = [
        [(500, 100), (620, 100), (620, 300), (500, 300), (500, 100)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Drehpunkt in der Nähe der Kiste
        world.add_static_segment((850, floor_y), (850, floor_y - 80), color=(120, 100, 80), radius=8)

        # Dynamischer Hebelbalken auf dem Drehpunkt
        world.add_dynamic_box((850, floor_y - 95), width=700, height=24, mass=4.0, color=(160, 110, 70))

        # Schwere Kiste auf dem rechten Ende des Hebels
        world.add_dynamic_box((1050, floor_y - 170), width=140, height=120, mass=6.0, color=(170, 105, 55))

    def check_victory(self, world: PhysicsWorld, dt: float = 0.0) -> bool:
        if not world.dynamic_boxes:
            return False
        # Die Kiste ist das oberste dynamische Objekt auf dem Hebel
        box = world.dynamic_boxes[-1]
        return box.is_lifted

