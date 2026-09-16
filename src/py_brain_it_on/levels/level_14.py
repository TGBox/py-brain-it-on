"""
Level 14 — Wippen-Transfer

Eine vorinstallierte Holzwippe balanciert in der Mitte des Spielfelds.
Der Ball muss auf die Wippe gebracht werden, damit sie kippt und ihn ins Ziel befördert.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_GREEN, WINDOW_WIDTH, WINDOW_HEIGHT


class Level14(BaseLevel):
    LEVEL_NUMBER = 14
    TITLE = "Wippen-Transfer"
    GOAL_DESCRIPTION = "Nutze die Wippe, um den Ball zum Eimer zu befördern!"
    HINT = "Leite den Ball auf die linke Seite der Wippe oder beschwere die rechte Seite mit einem Gewicht."
    BG_COLOR = (244, 248, 240)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Start-Podest links oben
        world.add_static_segment((120, 320), (420, 320), color=(140, 120, 100), radius=6)
        world.add_ball((270, 270), color=COLOR_CORAL)

        # Drehpunkt / Stütze für die Wippe
        world.add_static_segment((960, 640), (940, 680), color=COLOR_GREEN, radius=8)
        world.add_static_segment((960, 640), (980, 680), color=COLOR_GREEN, radius=8)
        world.add_static_segment((930, 680), (990, 680), color=COLOR_GREEN, radius=6)

        # Balancierender Wippbalken
        world.add_dynamic_box((960, 625), width=520, height=22, mass=4.0, color=(160, 110, 70))

        # Eimer unten rechts
        world.add_bucket((1600, floor_y), width=160, height=120, color=COLOR_TEAL)
