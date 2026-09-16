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
    SOLUTION_DESCRIPTION = "Flipper-Katapult: Ein fallendes Gewicht trifft die Wippe und katapultiert den Ball auf das Podest."
    SOLUTION_STROKES = [
        [(380, 200), (460, 200), (460, 300), (380, 300), (380, 200)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Durchgehender Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

        # Flipper-Katapult: Drehpunkt und Wippe
        world.add_static_segment((600, floor_y), (600, floor_y - 70), color=COLOR_PURPLE, radius=8)
        world.add_dynamic_box((600, floor_y - 85), width=520, height=22, mass=4.0, color=(160, 110, 70))
        world.add_ball((780, floor_y - 120), color=COLOR_CORAL)

        # Erhöhtes Podest rechts für den Eimer
        world.add_static_segment((1200, 440), (1500, 440), color=(140, 120, 100), radius=6)
        world.add_bucket((1350, 440), width=150, height=120, color=COLOR_TEAL)
