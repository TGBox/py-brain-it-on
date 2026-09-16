"""
Level 19 — Turmsturz

Eine hohe, schlanke Säule balanciert auf einem Podest in der Mitte.
Kein Eimer — das Ziel ist rein physikalische Zerstörungskraft!
Ziel: Bringe die rote Säule zum Umkippen!
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import WINDOW_WIDTH, WINDOW_HEIGHT


class Level19(BaseLevel):
    LEVEL_NUMBER = 19
    TITLE = "Turmsturz"
    GOAL_DESCRIPTION = "Bringe die rote Säule zum Umstürzen!"
    HINT = "Lass ein schweres Gewicht von oben seitlich gegen die Säule krachen oder baue einen massiven Pendelarm."
    BG_COLOR = (248, 240, 236)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Sockel für die Säule
        world.add_static_segment((800, 880), (1120, 880), color=(140, 120, 100), radius=8)

        # Schlanke, hohe Säule (Höhe 360px)
        world.add_dynamic_pillar((960, 700), width=45, height=360, mass=3.0, color=(225, 95, 60))

    def check_victory(self, world: PhysicsWorld, dt: float = 0.0) -> bool:
        if not world.dynamic_boxes:
            return False
        pillar = world.dynamic_boxes[0]
        return pillar.is_toppled
