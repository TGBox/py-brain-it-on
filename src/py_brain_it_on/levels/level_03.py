"""
Level 3 — Trichter

Ball faellt frei von oben.
Eimer hat eine enge Oeffnung, die schwer zu treffen ist.
Ziel: Einen Trichter zeichnen, der den Ball in den Eimer lenkt.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_PURPLE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level03(BaseLevel):
    LEVEL_NUMBER = 3
    TITLE = "Trichter"
    HINT = "Zeichne zwei schraege Linien als Trichter ueber dem Eimer."
    BG_COLOR = (242, 238, 250)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        # Ball faellt von oben
        world.add_ball((W // 2 - 80, 80), color=COLOR_CORAL)

        # Enger Eimer in der Mitte unten
        world.add_bucket((W // 2, H - 80), width=55, height=65, color=COLOR_TEAL)

        # Boden-Plattformen links und rechts (Eimer freigeben)
        world.add_static_segment((0, H - 80), (W // 2 - 60, H - 80), color=(140, 120, 100), radius=5)
        world.add_static_segment((W // 2 + 60, H - 80), (W, H - 80), color=(140, 120, 100), radius=5)

        # Leitrampen (Hilfe für die Aufgabe klarer machen)
        world.add_static_segment((60, 260), (150, 340), color=COLOR_PURPLE, radius=4)
        world.add_static_segment((W - 60, 260), (W - 150, 340), color=COLOR_PURPLE, radius=4)
