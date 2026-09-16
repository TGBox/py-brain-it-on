"""
Level 7 — Flipper-Stoß

Der Ball liegt tief in einer Nische gefangen.
Der Eimer befindet sich erhöht auf einem Podest rechts.
Ziel: Den Ball mit Wucht aus der Nische nach oben schleudern.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_PURPLE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level07(BaseLevel):
    LEVEL_NUMBER = 7
    TITLE = "Flipper-Stoß"
    GOAL_DESCRIPTION = "Katapultiere den Ball aus der Nische auf das Podest!"
    HINT = "Lass ein schweres Objekt oder einen Keil auf den Ball fallen, um ihn herauszukatapultieren."
    BG_COLOR = (242, 246, 250)
    STAR_THRESHOLDS = (1, 2)

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Boden links und Mitte
        world.add_static_segment((0, floor_y), (350, floor_y), color=(140, 120, 100), radius=6)

        # Nische für den Ball
        world.add_static_segment((350, floor_y), (350, floor_y - 280), color=COLOR_PURPLE, radius=8)
        world.add_static_segment((650, floor_y), (650, floor_y - 180), color=COLOR_PURPLE, radius=8)
        world.add_static_segment((350, floor_y), (650, floor_y), color=(140, 120, 100), radius=6)
        world.add_ball((500, floor_y - 50), color=COLOR_CORAL)

        # Restlicher Boden
        world.add_static_segment((650, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Erhöhtes Podest rechts für den Eimer
        world.add_static_segment((1280, 520), (1750, 520), color=(140, 120, 100), radius=6)
        world.add_bucket((1520, 520), width=150, height=120, color=COLOR_TEAL)
