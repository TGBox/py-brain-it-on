"""
Level 22 — Domino-Effekt

Zwei Säulen stehen hintereinander aufgereiht.
Ziel: Bring beide Säulen durch eine Kettenreaktion zum Umstürzen!
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import WINDOW_WIDTH, WINDOW_HEIGHT


class Level22(BaseLevel):
    LEVEL_NUMBER = 22
    TITLE = "Domino-Effekt"
    GOAL_DESCRIPTION = "Bringe beide Säulen zum Umstürzen!"
    HINT = "Kippe die erste rote Säule nach rechts, damit sie die blaue Säule mitreißt."
    BG_COLOR = (248, 244, 240)
    STAR_THRESHOLDS = (1, 2)
    SOLUTION_DESCRIPTION = "Ein herabstürzendes Gewicht bringt die rote Säule zum Kippen, die wiederum wie ein Domino die blaue Säule umwirft."
    SOLUTION_STROKES = [
        [(680, 200), (740, 200), (740, 350), (680, 350), (680, 200)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Säule 1 (rot)
        world.add_dynamic_pillar((750, floor_y - 140), width=40, height=280, mass=3.0, color=(220, 90, 60))

        # Säule 2 (blau)
        world.add_dynamic_pillar((1000, floor_y - 140), width=40, height=280, mass=3.0, color=(60, 130, 210))

    def check_victory(self, world: PhysicsWorld, dt: float = 0.0) -> bool:
        if len(world.dynamic_boxes) < 2:
            return False
        return all(p.is_toppled for p in world.dynamic_boxes)
