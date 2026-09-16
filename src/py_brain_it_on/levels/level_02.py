"""
Level 2 — Bogenbruecke

Ball liegt links. Ein Hindernis (Wand) steht in der Mitte.
Eimer steht rechts dahinter.
Ziel: Eine Bruecke ueber das Hindernis zeichnen oder einen Bogen.
"""
from __future__ import annotations

import pygame

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_ORANGE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level02(BaseLevel):
    LEVEL_NUMBER = 2
    TITLE = "Bogenbruecke"
    HINT = "Nutze einen Hebel oder ein fallendes Gewicht, um den Ball ueber die Wand zu katapultieren."
    BG_COLOR = (245, 240, 232)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        # Boden
        world.add_static_segment((0, H - 80), (W, H - 80), color=(140, 120, 100), radius=5)

        # Ball-Plattform links
        world.add_static_segment((40, 300), (180, 300), color=(140, 120, 100), radius=5)
        world.add_ball((110, 265), color=COLOR_CORAL)

        # Hindernis-Wand in der Mitte
        world.add_static_segment((360, H - 80), (360, 260), color=COLOR_ORANGE, radius=8)
        world.add_static_segment((360, 260), (340, 240), color=COLOR_ORANGE, radius=8)  # leicht schräge Spitze

        # Eimer rechts
        world.add_bucket((600, H - 80), width=80, height=65, color=COLOR_TEAL)
