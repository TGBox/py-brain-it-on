"""
Level 25 — Großes Finale

Das Meister-Puzzle:
Eine massive Mittelsäule versperrt den Weg und muss gestürzt werden,
während gleichzeitig zwei Bälle von den Außenseiten in den zentralen Eimer rollen müssen!
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_BLUE, COLOR_TEAL, WINDOW_WIDTH, WINDOW_HEIGHT


class Level25(BaseLevel):
    LEVEL_NUMBER = 25
    TITLE = "Großes Finale"
    GOAL_DESCRIPTION = "Stürze die Säule um und versenke beide Bälle im Eimer!"
    HINT = "Bringe die Mittelsäule zum Umfallen und baue zwei Rutschen, die beide Bälle in den Eimer leiten."
    BG_COLOR = (246, 240, 235)
    STAR_THRESHOLDS = (1, 3)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Ball 1 oben links
        world.add_static_segment((120, 320), (450, 320), color=(140, 120, 100), radius=6)
        world.add_ball((280, 270), color=COLOR_CORAL)

        # Ball 2 oben rechts
        world.add_static_segment((W - 450, 320), (W - 120, 320), color=(140, 120, 100), radius=6)
        world.add_ball((W - 280, 270), color=COLOR_BLUE)

        # Mittelsockel mit hoher Säule
        world.add_static_segment((800, 680), (1120, 680), color=(140, 120, 100), radius=8)
        world.add_dynamic_pillar((960, 490), width=45, height=380, mass=3.5, color=(220, 90, 60))

        # Großer Ziel-Eimer unten in der Mitte
        world.add_bucket((W // 2, floor_y), width=220, height=130, color=COLOR_TEAL)

        # Boden links und rechts
        world.add_static_segment((0, floor_y), (W // 2 - 130, floor_y), color=(140, 120, 100), radius=6)
        world.add_static_segment((W // 2 + 130, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

    def check_victory(self, world: PhysicsWorld, dt: float = 0.0) -> bool:
        if not world.dynamic_boxes:
            return False
        pillar = world.dynamic_boxes[0]
        return pillar.is_toppled and world.all_balls_in_bucket
