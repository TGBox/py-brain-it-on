"""
physics/world.py — pymunk-Physikwelt-Wrapper für Brain it on!

Verwaltet:
- Physik-Space (Gravitation, Damping)
- Ball-Objekte (Dynamic Circles)
- Statische Objekte (Plattformen, Wände, Eimer)
- Kollisionserkennung: Ball im Eimer
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import pymunk
import pygame

from ..settings import (
    GRAVITY, PHYSICS_DAMPING,
    BALL_RADIUS, BALL_MASS, BALL_ELASTICITY, BALL_FRICTION,
    WALL_FRICTION, WALL_ELASTICITY, SEGMENT_RADIUS,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_CORAL, COLOR_TEAL, COLOR_YELLOW, COLOR_BLUE,
    COLOR_WHITE, COLOR_TEXT, COLOR_BG_DARK,
)

# Kollisions-Typen
CTYPE_BALL   = 1
CTYPE_BUCKET = 2
CTYPE_WALL   = 3
CTYPE_DRAWN  = 4


@dataclass
class BallState:
    body: pymunk.Body
    shape: pymunk.Circle
    color: tuple = field(default_factory=lambda: COLOR_CORAL)
    in_bucket: bool = False


@dataclass
class DrawnStroke:
    """Eine vom Spieler gezeichnete Linie als Physik-Segmente."""
    points: list[tuple[float, float]]          # Rohpunkte
    segments: list[pymunk.Segment] = field(default_factory=list)
    body: Optional[pymunk.Body] = None
    color: tuple = (80, 70, 65)
    is_static: bool = False


class PhysicsWorld:
    """
    Kapselt eine pymunk.Space-Instanz mit Hilfsmethoden
    für das Ball-in-Eimer-Spielprinzip.
    """

    def __init__(self) -> None:
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        self.space.damping = PHYSICS_DAMPING

        self.balls: list[BallState] = []
        self.drawn_strokes: list[DrawnStroke] = []
        self.bucket_sensor_shape: Optional[pymunk.Shape] = None
        self._bucket_rect: Optional[tuple] = None  # (x, y, w, h) zum Zeichnen
        self._static_draw_items: list[tuple] = []  # (type, args, color) zum Zeichnen
        self._level_static_shapes: list[pymunk.Shape] = []  # Für Verankerungstests

        self._balls_in_bucket: set[int] = set()    # IDs der Bälle im Eimer

        # Kollisions-Handler Ball ↔ Eimer-Sensor
        self.space.on_collision(
            CTYPE_BALL,
            CTYPE_BUCKET,
            begin=self._on_ball_enter_bucket,
            separate=self._on_ball_exit_bucket,
        )

        # Unsichtbare Außenwände
        self._add_border_walls()

    # ------------------------------------------------------------------
    # Physik-Schritt
    # ------------------------------------------------------------------

    def step(self, dt: float) -> None:
        """Simuliert einen Physik-Schritt."""
        steps = 3  # Sub-Stepping für Stabilität
        sub_dt = dt / steps
        for _ in range(steps):
            self.space.step(sub_dt)
        # Status aktualisieren
        for ball in self.balls:
            ball.in_bucket = id(ball.body) in self._balls_in_bucket

    # ------------------------------------------------------------------
    # Ball hinzufügen
    # ------------------------------------------------------------------

    def add_ball(
        self,
        pos: tuple[float, float],
        color: tuple = COLOR_CORAL,
        velocity: tuple[float, float] = (0, 0),
    ) -> BallState:
        moment = pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS)
        body = pymunk.Body(BALL_MASS, moment)
        body.position = pos
        body.velocity = velocity
        shape = pymunk.Circle(body, BALL_RADIUS)
        shape.elasticity = BALL_ELASTICITY
        shape.friction = BALL_FRICTION
        shape.collision_type = CTYPE_BALL
        self.space.add(body, shape)
        state = BallState(body=body, shape=shape, color=color)
        self.balls.append(state)
        return state

    # ------------------------------------------------------------------
    # Statische Segmente (Plattformen, Wände)
    # ------------------------------------------------------------------

    def add_static_segment(
        self,
        a: tuple[float, float],
        b: tuple[float, float],
        color: tuple = (80, 75, 70),
        radius: float = 5,
    ) -> pymunk.Segment:
        seg = pymunk.Segment(self.space.static_body, a, b, radius)
        seg.elasticity = WALL_ELASTICITY
        seg.friction = WALL_FRICTION
        seg.collision_type = CTYPE_WALL
        self.space.add(seg)
        self._static_draw_items.append(("segment", (a, b, radius), color))
        self._level_static_shapes.append(seg)
        return seg

    def add_static_box(
        self,
        rect: tuple[float, float, float, float],
        color: tuple = (100, 95, 90),
    ) -> None:
        """Fügt eine statische rechteckige Plattform hinzu."""
        x, y, w, h = rect
        corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        box_segs = []
        for i in range(len(corners)):
            a = corners[i]
            b = corners[(i + 1) % len(corners)]
            seg = pymunk.Segment(self.space.static_body, a, b, 2)
            seg.elasticity = WALL_ELASTICITY
            seg.friction = WALL_FRICTION
            seg.collision_type = CTYPE_WALL
            self.space.add(seg)
            box_segs.append(seg)
        self._static_draw_items.append(("box", rect, color))
        self._level_static_shapes.extend(box_segs)

    # ------------------------------------------------------------------
    # Eimer
    # ------------------------------------------------------------------

    def add_bucket(
        self,
        pos: tuple[float, float],
        width: float = 70,
        height: float = 60,
        color: tuple = COLOR_TEAL,
    ) -> None:
        """
        Fügt einen Eimer hinzu (zwei Seitenwände + Boden + Sensor im Inneren).
        pos = (cx, cy) = Mittelpunkt des Eimer-Bodens.
        """
        cx, cy = pos
        hw = width / 2
        # Boden
        seg_bottom = pymunk.Segment(self.space.static_body, (cx - hw, cy), (cx + hw, cy), 4)
        seg_bottom.elasticity = 0.1
        seg_bottom.friction = 0.8
        seg_bottom.collision_type = CTYPE_WALL
        # Linke Wand
        seg_left = pymunk.Segment(self.space.static_body, (cx - hw, cy - height), (cx - hw, cy), 4)
        seg_left.elasticity = 0.1
        seg_left.friction = 0.8
        seg_left.collision_type = CTYPE_WALL
        # Rechte Wand
        seg_right = pymunk.Segment(self.space.static_body, (cx + hw, cy - height), (cx + hw, cy), 4)
        seg_right.elasticity = 0.1
        seg_right.friction = 0.8
        seg_right.collision_type = CTYPE_WALL
        self.space.add(seg_bottom, seg_left, seg_right)
        self._level_static_shapes.extend([seg_bottom, seg_left, seg_right])

        # Unsichtbarer Sensor im Eimer (Siegbedingung)
        sensor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        sensor_shape = pymunk.Poly.create_box(sensor_body, (width - 8, height - 8))
        sensor_body.position = (cx, cy - height / 2)
        sensor_shape.sensor = True
        sensor_shape.collision_type = CTYPE_BUCKET
        self.space.add(sensor_body, sensor_shape)
        self.bucket_sensor_shape = sensor_shape

        self._bucket_rect = (cx - hw, cy - height, width, height)
        self._static_draw_items.append(("bucket", (cx, cy, hw, height, color), color))

    # ------------------------------------------------------------------
    # Gezeichnete Linien als Physik
    # ------------------------------------------------------------------

    def _is_point_connected_to_static(self, p: tuple[float, float], threshold: float = 8.0) -> bool:
        """Prüft, ob ein Punkt nahe an einem statischen Level-Objekt oder statischem Strich liegt."""
        v = pymunk.Vec2d(*p)
        for shape in self._level_static_shapes:
            info = shape.point_query(v)
            if info.distance <= threshold:
                return True
        return False

    @staticmethod
    def _compute_stroke_physics(points: list[tuple[float, float]], radius: float = SEGMENT_RADIUS):
        """Berechnet Schwerpunkt, Masse und Trägheitsmoment für dynamische Striche."""
        seg_lengths = []
        total_length = 0.0
        for i in range(len(points) - 1):
            p1 = pymunk.Vec2d(*points[i])
            p2 = pymunk.Vec2d(*points[i + 1])
            l = p1.get_distance(p2)
            seg_lengths.append(l)
            total_length += l

        if total_length < 1e-4:
            total_length = 1.0
            seg_lengths = [1.0]

        com = pymunk.Vec2d(0, 0)
        for i in range(len(points) - 1):
            p1 = pymunk.Vec2d(*points[i])
            p2 = pymunk.Vec2d(*points[i + 1])
            com += (p1 + p2) * 0.5 * seg_lengths[i]
        com = com / total_length

        # Dichte: ca. 0.025 kg/px, Mindestmasse 0.8 kg
        mass = max(0.8, total_length * 0.025)

        total_moment = 0.0
        local_segments = []
        for i in range(len(points) - 1):
            p1_local = pymunk.Vec2d(*points[i]) - com
            p2_local = pymunk.Vec2d(*points[i + 1]) - com
            seg_mass = mass * (seg_lengths[i] / total_length)
            seg_moment = pymunk.moment_for_segment(seg_mass, p1_local, p2_local, radius)
            total_moment += seg_moment
            local_segments.append((p1_local, p2_local))

        total_moment = max(20.0, total_moment)
        return com, mass, total_moment, local_segments

    def add_drawn_stroke(self, points: list[tuple[float, float]], color: tuple = (80, 70, 65)) -> DrawnStroke:
        """
        Fügt eine gezeichnete Polyline in die Physikwelt ein.
        Hängt die Form an einem statischen Level-Objekt (Start- oder Endpunkt berührt Plattform/Wand),
        wird sie als statischer Körper verankert.
        Andernfalls wird sie zu einem dynamischen Physikobjekt (kann fallen, hebeln, Bälle stoßen).
        """
        if len(points) < 2:
            return DrawnStroke(points=points, color=color)

        is_connected = (
            self._is_point_connected_to_static(points[0])
            or self._is_point_connected_to_static(points[-1])
        )

        if is_connected:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            segments = []
            for i in range(len(points) - 1):
                seg = pymunk.Segment(body, points[i], points[i + 1], SEGMENT_RADIUS)
                seg.elasticity = WALL_ELASTICITY
                seg.friction = WALL_FRICTION
                seg.collision_type = CTYPE_DRAWN
                segments.append(seg)
            self.space.add(body, *segments)
            self._level_static_shapes.extend(segments)
            stroke = DrawnStroke(points=points, segments=segments, body=body, color=color, is_static=True)
        else:
            com, mass, moment, local_segs = self._compute_stroke_physics(points)
            body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
            body.position = (com.x, com.y)
            segments = []
            for p1_local, p2_local in local_segs:
                seg = pymunk.Segment(body, p1_local, p2_local, SEGMENT_RADIUS)
                seg.elasticity = 0.35
                seg.friction = 0.7
                seg.collision_type = CTYPE_DRAWN
                segments.append(seg)
            self.space.add(body, *segments)
            stroke = DrawnStroke(points=points, segments=segments, body=body, color=color, is_static=False)

        self.drawn_strokes.append(stroke)
        return stroke

    def remove_drawn_strokes(self) -> None:
        """Entfernt alle vom Spieler gezeichneten Linien."""
        for stroke in self.drawn_strokes:
            if stroke.body:
                for seg in stroke.segments:
                    if seg in self.space.shapes:
                        self.space.remove(seg)
                    if seg in self._level_static_shapes:
                        self._level_static_shapes.remove(seg)
                if stroke.body in self.space.bodies:
                    self.space.remove(stroke.body)
        self.drawn_strokes.clear()

    def remove_all_dynamic(self) -> None:
        """Entfernt alle Bälle (für Reset)."""
        for ball in self.balls:
            if ball.shape in self.space.shapes:
                self.space.remove(ball.shape)
            if ball.body in self.space.bodies:
                self.space.remove(ball.body)
        self.balls.clear()
        self._balls_in_bucket.clear()

    # ------------------------------------------------------------------
    # Siegbedingung
    # ------------------------------------------------------------------

    @property
    def all_balls_in_bucket(self) -> bool:
        """True wenn alle Bälle im Eimer und (fast) zur Ruhe gekommen sind."""
        if not self.balls:
            return False
        for ball in self.balls:
            if not ball.in_bucket:
                return False
            speed = ball.body.velocity.length
            if speed > 80:
                return False
        return True

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet alle Physik-Objekte auf die Surface."""
        # Statische Objekte
        for item_type, args, color in self._static_draw_items:
            if item_type == "segment":
                a, b, r = args
                self._draw_segment(surface, a, b, r, color)
            elif item_type == "box":
                x, y, w, h = args
                pygame.draw.rect(surface, color, (int(x), int(y), int(w), int(h)), border_radius=4)
            elif item_type == "bucket":
                self._draw_bucket(surface, args, color)

        # Gezeichnete Striche
        for stroke in self.drawn_strokes:
            for seg in stroke.segments:
                world_a = seg.body.local_to_world(seg.a)
                world_b = seg.body.local_to_world(seg.b)
                self._draw_segment(
                    surface,
                    (world_a.x, world_a.y),
                    (world_b.x, world_b.y),
                    SEGMENT_RADIUS + 1,
                    stroke.color,
                )

            # Wenn statisch: Dezente Verankerungspunkte an den Kontaktstellen
            if stroke.is_static and stroke.segments:
                p_start = stroke.segments[0].body.local_to_world(stroke.segments[0].a)
                p_end = stroke.segments[-1].body.local_to_world(stroke.segments[-1].b)
                for pt in (p_start, p_end):
                    if self._is_point_connected_to_static((pt.x, pt.y), threshold=18.0):
                        pygame.draw.circle(surface, (50, 45, 40), (int(pt.x), int(pt.y)), SEGMENT_RADIUS + 3)
                        pygame.draw.circle(surface, (230, 220, 200), (int(pt.x), int(pt.y)), SEGMENT_RADIUS + 1)

        # Bälle
        for ball in self.balls:
            pos = ball.body.position
            cx, cy = int(pos.x), int(pos.y)
            r = BALL_RADIUS
            # Schatten
            shadow_surf = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surf, (0, 0, 0, 40), (r + 3, r + 5), r)
            surface.blit(shadow_surf, (cx - r - 3, cy - r - 3))
            # Ball
            pygame.draw.circle(surface, ball.color, (cx, cy), r)
            # Glanzpunkt
            highlight_r = max(4, r // 3)
            pygame.draw.circle(surface, (255, 255, 255), (cx - r // 3, cy - r // 3), highlight_r)
            pygame.draw.circle(surface, (255, 255, 255), (cx - r // 3, cy - r // 3), highlight_r - 2)
            # Umriss
            pygame.draw.circle(surface, tuple(max(0, c - 40) for c in ball.color), (cx, cy), r, 2)

    def _draw_segment(
        self,
        surface: pygame.Surface,
        a: tuple, b: tuple, r: float, color: tuple
    ) -> None:
        ax, ay = int(a[0]), int(a[1])
        bx, by = int(b[0]), int(b[1])
        ri = max(2, int(r))
        if ax == bx and ay == by:
            pygame.draw.circle(surface, color, (ax, ay), ri)
            return
        # Linie mit abgerundeten Enden
        pygame.draw.line(surface, color, (ax, ay), (bx, by), ri * 2)
        pygame.draw.circle(surface, color, (ax, ay), ri)
        pygame.draw.circle(surface, color, (bx, by), ri)

    def _draw_bucket(self, surface: pygame.Surface, args: tuple, color: tuple) -> None:
        cx, cy, hw, height, col = args
        # Füllung (halbtransparent)
        fill_surf = pygame.Surface((int(hw * 2 - 8), int(height - 4)), pygame.SRCALPHA)
        fill_surf.fill((*col, 30))
        surface.blit(fill_surf, (int(cx - hw + 4), int(cy - height + 2)))
        # Wände des Eimers
        thick = 6
        left_x, right_x = int(cx - hw), int(cx + hw)
        bottom_y = int(cy)
        top_y = int(cy - height)
        pygame.draw.line(surface, col, (left_x, top_y), (left_x, bottom_y), thick)
        pygame.draw.line(surface, col, (right_x, top_y), (right_x, bottom_y), thick)
        pygame.draw.line(surface, col, (left_x, bottom_y), (right_x, bottom_y), thick)
        # Griff (obere Öffnung andeuten)
        handle_col = tuple(max(0, c - 30) for c in col)
        pygame.draw.line(surface, handle_col, (left_x - 2, top_y), (left_x + 10, top_y), 3)
        pygame.draw.line(surface, handle_col, (right_x + 2, top_y), (right_x - 10, top_y), 3)

    # ------------------------------------------------------------------
    # Interne Hilfsmethoden
    # ------------------------------------------------------------------

    def _add_border_walls(self) -> None:
        """Unsichtbare Außenwände des Spielfelds (etwas außerhalb des sichtbaren Bereichs)."""
        w, h = WINDOW_WIDTH, WINDOW_HEIGHT
        margin = 20
        segs = [
            # Boden
            ((-margin, h + margin), (w + margin, h + margin)),
            # Links
            ((-margin, -margin), (-margin, h + margin)),
            # Rechts
            ((w + margin, -margin), (w + margin, h + margin)),
            # Oben (als offener Bereich, Bälle können nach oben fliegen)
            # (kein oberer Wall → Bälle die zu weit fliegen fallen einfach zurück)
        ]
        for a, b in segs:
            seg = pymunk.Segment(self.space.static_body, a, b, 2)
            seg.elasticity = WALL_ELASTICITY
            seg.friction = WALL_FRICTION
            seg.collision_type = CTYPE_WALL
            self.space.add(seg)

    def _on_ball_enter_bucket(
        self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict
    ) -> bool:
        for shape in arbiter.shapes:
            if shape.collision_type == CTYPE_BALL and hasattr(shape, 'body'):
                self._balls_in_bucket.add(id(shape.body))
                for ball in self.balls:
                    if ball.body is shape.body:
                        ball.in_bucket = True
        return True

    def _on_ball_exit_bucket(
        self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict
    ) -> None:
        for shape in arbiter.shapes:
            if shape.collision_type == CTYPE_BALL and hasattr(shape, 'body'):
                self._balls_in_bucket.discard(id(shape.body))
                for ball in self.balls:
                    if ball.body is shape.body:
                        ball.in_bucket = False
