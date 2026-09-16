"""
Level 18 — Der Tunnel

Der Ball muss durch einen schmalen, überdachten Tunnel rollen.
Zu steile Kurven lassen den Ball an der Tunneldecke abprallen und abstürzen.
"""
from __future__ import annotations

from .base_level import BaseLevel
from ..physics.world import PhysicsWorld
from ..settings import COLOR_CORAL, COLOR_TEAL, COLOR_ORANGE, WINDOW_WIDTH, WINDOW_HEIGHT


class Level18(BaseLevel):
    LEVEL_NUMBER = 18
    TITLE = "Der Tunnel"
    GOAL_DESCRIPTION = "Führe den Ball durch den überdachten Tunnel in den Eimer!"
    HINT = "Zeichne eine sanfte, flache Rampe, die den Ball geradewegs durch den Tunnel gleiten lässt."
    BG_COLOR = (244, 242, 238)
    STAR_THRESHOLDS = (1, 2)
    SOLUTION_DESCRIPTION = "Eine sanft abfallende Rutsche führt den Ball präzise durch den engen Tunnel direkt in den Eimer."
    SOLUTION_STROKES = [
        [(240, 360), (280, 450), (450, 560), (640, 660), (1000, 715), (1400, 720), (1500, 730), (1630, 780)]
    ]

    def setup(self, world: PhysicsWorld) -> None:
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        floor_y = H - 90

        # Start-Podest links
        world.add_static_segment((120, 460), (450, 460), color=(140, 120, 100), radius=6)
        world.add_ball((280, 410), color=COLOR_CORAL)

        # Tunnel: Boden & Decke
        world.add_static_segment((650, 740), (1400, 740), color=(140, 120, 100), radius=8)
        world.add_static_segment((700, 600), (1350, 600), color=COLOR_ORANGE, radius=8)

        # Eimer rechts auf Anschluss-Podest (abgesenkt, damit Korböffnung auf Tunnelhöhe liegt)
        world.add_static_segment((1450, 860), (1850, 860), color=(140, 120, 100), radius=6)
        world.add_bucket((1650, 860), width=160, height=120, color=COLOR_TEAL)

        # Tiefer Boden
        world.add_static_segment((0, floor_y), (W, floor_y), color=(140, 120, 100), radius=6)

