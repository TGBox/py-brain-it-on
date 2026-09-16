"""
physics/drawing.py — Konvertierung von Maus-Eingaben zu Physik-Objekten.

Pipeline:
1. Während Maus gedrückt: Punkte sammeln (raw_points)
2. Bei Mausloslassen: Douglas-Peucker-Vereinfachung
3. Vereinfachte Punkte → PhysicsWorld.add_drawn_stroke()
"""
from __future__ import annotations

import math
from typing import Optional

import pygame

from ..settings import DRAW_SIMPLIFY_TOLERANCE, SEGMENT_RADIUS, COLOR_TEXT


def douglas_peucker(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    """
    Vereinfacht eine Polyline mit dem Douglas-Peucker-Algorithmus.
    Behält nur Punkte, die weiter als epsilon von der Verbindungslinie entfernt sind.
    """
    if len(points) < 3:
        return points

    # Maximalen Abstand finden
    max_dist = 0.0
    max_idx = 0
    start, end = points[0], points[-1]

    for i in range(1, len(points) - 1):
        dist = _point_to_line_dist(points[i], start, end)
        if dist > max_dist:
            max_dist = dist
            max_idx = i

    if max_dist > epsilon:
        # Rekursiv aufteilen
        left = douglas_peucker(points[:max_idx + 1], epsilon)
        right = douglas_peucker(points[max_idx:], epsilon)
        return left[:-1] + right
    else:
        return [start, end]


def _point_to_line_dist(
    point: tuple[float, float],
    line_start: tuple[float, float],
    line_end: tuple[float, float],
) -> float:
    """Abstand eines Punktes von einer Linie."""
    px, py = point
    ax, ay = line_start
    bx, by = line_end
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    nx, ny = ax + t * dx, ay + t * dy
    return math.hypot(px - nx, py - ny)


class DrawingManager:
    """
    Verwaltet den aktuellen Zeich-Vorgang des Spielers.

    Zustände:
    - idle: Keine Aktion
    - drawing: Maus gedrückt, Punkte werden gesammelt
    """

    MIN_POINT_DIST = 4.0   # Mindestabstand zwischen gespeicherten Punkten

    def __init__(self) -> None:
        self._drawing = False
        self._raw_points: list[tuple[float, float]] = []
        self._preview_color = (80, 70, 65)

    @property
    def is_drawing(self) -> bool:
        return self._drawing

    @property
    def current_points(self) -> list[tuple[float, float]]:
        return list(self._raw_points)

    def start(self, pos: tuple[int, int]) -> None:
        """Beginnt einen neuen Strich."""
        self._drawing = True
        self._raw_points = [tuple(map(float, pos))]

    def add_point(self, pos: tuple[int, int]) -> None:
        """Fügt einen Punkt hinzu (nur wenn Mindestabstand überschritten)."""
        if not self._drawing:
            return
        fp = tuple(map(float, pos))
        if self._raw_points:
            last = self._raw_points[-1]
            dist = math.hypot(fp[0] - last[0], fp[1] - last[1])
            if dist < self.MIN_POINT_DIST:
                return
        self._raw_points.append(fp)

    def finish(self) -> list[tuple[float, float]] | None:
        """
        Beendet den Strich und gibt die vereinfachten Punkte zurück.
        Gibt None zurück, wenn zu wenige Punkte vorhanden sind.
        """
        self._drawing = False
        if len(self._raw_points) < 2:
            self._raw_points = []
            return None
        simplified = douglas_peucker(self._raw_points, DRAW_SIMPLIFY_TOLERANCE)
        self._raw_points = []
        return simplified if len(simplified) >= 2 else None

    def cancel(self) -> None:
        """Bricht den aktuellen Strich ab."""
        self._drawing = False
        self._raw_points = []

    def draw_preview(self, surface: pygame.Surface) -> None:
        """Zeichnet die aktuelle, noch nicht abgeschlossene Linie als Vorschau."""
        if not self._drawing or len(self._raw_points) < 2:
            return
        pts = [(int(p[0]), int(p[1])) for p in self._raw_points]
        # Schatten-Linie (leicht versetzt)
        if len(pts) >= 2:
            pygame.draw.lines(surface, (0, 0, 0, 40), False, pts, (SEGMENT_RADIUS + 1) * 2 + 2)
        pygame.draw.lines(surface, self._preview_color, False, pts, (SEGMENT_RADIUS + 1) * 2)
        # Endpunkt-Kreis
        pygame.draw.circle(surface, self._preview_color, pts[-1], SEGMENT_RADIUS + 1)
