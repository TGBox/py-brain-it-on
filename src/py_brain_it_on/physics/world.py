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
import pymunk.autogeometry
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
    """Eine vom Spieler gezeichnete Linie oder ein geschlossener Block als Physik-Segmente/Polygone."""
    points: list[tuple[float, float]]          # Rohpunkte
    segments: list[pymunk.Segment] = field(default_factory=list)
    poly_shapes: list[pymunk.Poly] = field(default_factory=list)
    body: Optional[pymunk.Body] = None
    color: tuple = (80, 70, 65)
    is_static: bool = False
    is_closed: bool = False
    connection_points: list[tuple[float, float]] = field(default_factory=list)



@dataclass
class DynamicBox:
    """Ein dynamischer Kasten / Säule für Umwerf-, Hebe- oder Barriere-Puzzles."""
    body: pymunk.Body
    shape: pymunk.Poly
    width: float
    height: float
    color: tuple = (180, 110, 70)
    initial_y: float = 0.0
    initial_angle: float = 0.0

    @property
    def is_toppled(self) -> bool:
        """True wenn der Körper um mehr als 45 Grad gekippt ist."""
        angle_diff = abs(self.body.angle - self.initial_angle) % (2 * math.pi)
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff
        return angle_diff > math.radians(45)

    @property
    def is_lifted(self) -> bool:
        """True wenn der Körper mindestens 60px über seiner Startposition ist."""
        return self.body.position.y < (self.initial_y - 60)


class PhysicsWorld:
    """
    Kapselt eine pymunk.Space-Instanz mit Hilfsmethoden
    für das Ball-in-Eimer-Spielprinzip und Spezialpuzzles.
    """

    def __init__(self) -> None:
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        self.space.damping = PHYSICS_DAMPING

        self.balls: list[BallState] = []
        self.dynamic_boxes: list[DynamicBox] = []
        self.drawn_strokes: list[DrawnStroke] = []
        self.bucket_sensor_shape: Optional[pymunk.Shape] = None
        self._bucket_rect: Optional[tuple] = None  # (x, y, w, h) zum Zeichnen
        self._static_draw_items: list[tuple] = []  # (type, args, color) zum Zeichnen
        self._level_static_shapes: list[pymunk.Shape] = []  # Für Verankerungstests

        self._balls_in_bucket: set[int] = set()    # IDs der Bälle im Eimer
        self.balls_collided: bool = False

        # Kollisions-Handler Ball ↔ Eimer-Sensor
        self.space.on_collision(
            CTYPE_BALL,
            CTYPE_BUCKET,
            begin=self._on_ball_enter_bucket,
            separate=self._on_ball_exit_bucket,
        )
        # Kollisions-Handler Ball ↔ Ball
        self.space.on_collision(
            CTYPE_BALL,
            CTYPE_BALL,
            begin=self._on_ball_collide_ball,
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

    def add_dynamic_box(
        self,
        pos: tuple[float, float],
        width: float,
        height: float,
        mass: float = 2.0,
        color: tuple = (180, 110, 70),
        friction: float = 0.7,
        elasticity: float = 0.2,
    ) -> DynamicBox:
        """Fügt einen dynamischen Kasten (z. B. Säule, Kiste, Gegengewicht) hinzu."""
        cx, cy = pos
        moment = pymunk.moment_for_box(mass, (width, height))
        body = pymunk.Body(mass, moment)
        body.position = (cx, cy)
        shape = pymunk.Poly.create_box(body, (width, height), radius=1)
        shape.friction = friction
        shape.elasticity = elasticity
        shape.collision_type = CTYPE_WALL
        self.space.add(body, shape)

        dbox = DynamicBox(
            body=body,
            shape=shape,
            width=width,
            height=height,
            color=color,
            initial_y=cy,
            initial_angle=0.0,
        )
        self.dynamic_boxes.append(dbox)
        return dbox

    def add_dynamic_pillar(
        self,
        pos: tuple[float, float],
        width: float = 30,
        height: float = 160,
        mass: float = 2.5,
        color: tuple = (220, 100, 60),
    ) -> DynamicBox:
        """Fügt eine aufrecht stehende Säule zum Umwerfen hinzu."""
        return self.add_dynamic_box(pos, width, height, mass=mass, color=color, friction=0.8)

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

    def find_connection_points(self, points: list[tuple[float, float]], threshold: float = 16.0) -> list[tuple[float, float]]:
        """Findet alle Kontaktpunkte entlang des Strichs mit beliebigen statischen Oberflächen."""
        contact_pts: list[tuple[float, float]] = []
        # Alle gezeichneten Punkte sowie Zwischenschritte abtasten
        sampled_pts = list(points)
        for i in range(len(points) - 1):
            p1 = pymunk.Vec2d(*points[i])
            p2 = pymunk.Vec2d(*points[i + 1])
            dist = p1.get_distance(p2)
            if dist > 12.0:
                steps = int(dist // 8.0)
                for s in range(1, steps):
                    inter = p1 + (p2 - p1) * (s / steps)
                    sampled_pts.append((inter.x, inter.y))

        for pt in sampled_pts:
            v = pymunk.Vec2d(*pt)
            for shape in self._level_static_shapes:
                info = shape.point_query(v)
                if info.distance <= threshold:
                    cand = (info.point.x, info.point.y)
                    # Mindestabstand zu anderen Nieten, damit es aufgeräumt aussieht
                    if not any(pymunk.Vec2d(*c).get_distance(cand) < 20.0 for c in contact_pts):
                        contact_pts.append(cand)
                    break
        return contact_pts

    @staticmethod
    def _compute_polygon_centroid(verts: list[tuple[float, float]]) -> pymunk.Vec2d:
        """Berechnet den Schwerpunkt eines Polygons."""
        n = len(verts)
        if n == 0:
            return pymunk.Vec2d(0, 0)
        cx, cy, signed_area = 0.0, 0.0, 0.0
        for i in range(n):
            x0, y0 = verts[i]
            x1, y1 = verts[(i + 1) % n]
            a = x0 * y1 - x1 * y0
            signed_area += a
            cx += (x0 + x1) * a
            cy += (y0 + y1) * a
        signed_area *= 0.5
        if abs(signed_area) < 1e-4:
            return pymunk.Vec2d(sum(v[0] for v in verts) / n, sum(v[1] for v in verts) / n)
        return pymunk.Vec2d(cx / (6.0 * signed_area), cy / (6.0 * signed_area))

    @staticmethod
    def _compute_stroke_physics(points: list[tuple[float, float]], radius: float = SEGMENT_RADIUS):
        """
        Berechnet Schwerpunkt, Masse und Trägheitsmoment.
        Erkennt geschlossene Formen (Start ~ Ende) und berechnet flächenbasierte Masse
        inklusive konvexer Polygon-Zerlegung. Offene Formen erhalten längenbasierte Masse.
        """
        is_closed = False
        local_polys: list[list[pymunk.Vec2d]] = []
        closed_pts = list(points)

        if len(points) >= 4:
            d_ends = pymunk.Vec2d(*points[0]).get_distance(pymunk.Vec2d(*points[-1]))
            if d_ends <= 24.0 or points[0] == points[-1]:
                closed_pts[-1] = closed_pts[0]
                verts = [pymunk.Vec2d(*p) for p in closed_pts[:-1]]
                signed_area = pymunk.area_for_poly(verts)
                area = abs(signed_area)
                if area >= 90.0:
                    if signed_area < 0:
                        closed_pts = list(reversed(closed_pts))
                        verts = [pymunk.Vec2d(*p) for p in closed_pts[:-1]]
                    try:
                        decomp = pymunk.autogeometry.convex_decomposition(closed_pts, 1.5)
                        if decomp:
                            com = PhysicsWorld._compute_polygon_centroid([(v.x, v.y) for v in verts])
                            # Flächenbasierte Masse: Dichte ~0.0022 kg/px²
                            mass = max(3.5, area * 0.0022)
                            total_moment = 0.0
                            for piece in decomp:
                                raw_piece = piece[:-1] if piece[0] == piece[-1] else piece
                                local_piece = [p - com for p in raw_piece]
                                if pymunk.area_for_poly(local_piece) < 0:
                                    local_piece = list(reversed(local_piece))
                                p_area = abs(pymunk.area_for_poly(local_piece))
                                p_mass = mass * (p_area / area) if area > 0 else mass
                                total_moment += pymunk.moment_for_poly(p_mass, local_piece)
                                local_polys.append(local_piece)
                            total_moment = max(40.0, total_moment)
                            is_closed = True
                    except Exception:
                        is_closed = False

        if is_closed and local_polys:
            local_segments = []
            return com, mass, total_moment, local_segments, True, local_polys

        # Offene Linie: Masse proportional zur Gesamtlänge
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
        return com, mass, total_moment, local_segments, False, []

    def add_drawn_stroke(self, points: list[tuple[float, float]], color: tuple = (80, 70, 65)) -> DrawnStroke:
        """
        Fügt eine gezeichnete Form (Polyline oder Block) in die Physikwelt ein.
        Berührt die Form statische Oberflächen, wird sie als statischer Körper verankert.
        Andernfalls wird sie zu einem dynamischen Physikobjekt.
        Geschlossene Formen werden als massive Polygone mit flächenbasierter Masse erzeugt.
        """
        if len(points) < 2:
            return DrawnStroke(points=points, color=color)

        conn_pts = self.find_connection_points(points, threshold=16.0)
        is_connected = len(conn_pts) > 0
        com, mass, moment, local_segs, is_closed, local_polys = self._compute_stroke_physics(points)

        if is_connected:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            segments = []
            polys = []
            if is_closed and local_polys:
                for piece in local_polys:
                    world_piece = [p + com for p in piece]
                    poly = pymunk.Poly(body, world_piece)
                    poly.elasticity = WALL_ELASTICITY
                    poly.friction = WALL_FRICTION
                    poly.collision_type = CTYPE_DRAWN
                    polys.append(poly)
                self.space.add(body, *polys)
                self._level_static_shapes.extend(polys)
            else:
                for i in range(len(points) - 1):
                    seg = pymunk.Segment(body, points[i], points[i + 1], SEGMENT_RADIUS)
                    seg.elasticity = WALL_ELASTICITY
                    seg.friction = WALL_FRICTION
                    seg.collision_type = CTYPE_DRAWN
                    segments.append(seg)
                self.space.add(body, *segments)
                self._level_static_shapes.extend(segments)

            stroke = DrawnStroke(
                points=points,
                segments=segments,
                poly_shapes=polys,
                body=body,
                color=color,
                is_static=True,
                is_closed=is_closed,
                connection_points=conn_pts,
            )
        else:
            body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
            body.position = (com.x, com.y)
            segments = []
            polys = []
            if is_closed and local_polys:
                for piece in local_polys:
                    poly = pymunk.Poly(body, piece)
                    poly.elasticity = 0.25
                    poly.friction = 0.75
                    poly.collision_type = CTYPE_DRAWN
                    polys.append(poly)
                self.space.add(body, *polys)
            else:
                for p1_local, p2_local in local_segs:
                    seg = pymunk.Segment(body, p1_local, p2_local, SEGMENT_RADIUS)
                    seg.elasticity = 0.35
                    seg.friction = 0.7
                    seg.collision_type = CTYPE_DRAWN
                    segments.append(seg)
                self.space.add(body, *segments)

            stroke = DrawnStroke(
                points=points,
                segments=segments,
                poly_shapes=polys,
                body=body,
                color=color,
                is_static=False,
                is_closed=is_closed,
                connection_points=[],
            )

        self.drawn_strokes.append(stroke)
        return stroke

    def pop_drawn_stroke(self) -> Optional[DrawnStroke]:
        """Entfernt den zuletzt gezeichneten Strich (Undo)."""
        if not self.drawn_strokes:
            return None
        stroke = self.drawn_strokes.pop()
        if stroke.body:
            for s in stroke.segments + stroke.poly_shapes:
                if s in self.space.shapes:
                    self.space.remove(s)
                if s in self._level_static_shapes:
                    self._level_static_shapes.remove(s)
            if stroke.body in self.space.bodies:
                self.space.remove(stroke.body)
        return stroke

    def get_connection_point_at(self, pos: tuple[float, float], threshold: float = 24.0) -> Optional[tuple[float, float]]:
        """Prüft, ob an der Position ein Verbindungspunkt liegt und gibt dessen Koordinaten zurück."""
        target_v = pymunk.Vec2d(*pos)
        for stroke in self.drawn_strokes:
            if not stroke.is_static or not stroke.connection_points:
                continue
            for cx, cy in stroke.connection_points:
                if target_v.get_distance(pymunk.Vec2d(cx, cy)) <= threshold:
                    return (cx, cy)
        return None

    def remove_connection_point_at(self, pos: tuple[float, float], threshold: float = 24.0) -> bool:
        """
        Löst einen Verbindungspunkt an der angegebenen Klick-Position.
        Sind alle Verbindungspunkte gelöst, wird der Strich automatisch zu einem dynamischen Physikobjekt.
        """
        target_v = pymunk.Vec2d(*pos)
        for stroke in self.drawn_strokes:
            if not stroke.is_static or not stroke.connection_points:
                continue
            for idx, (cx, cy) in enumerate(stroke.connection_points):
                if target_v.get_distance(pymunk.Vec2d(cx, cy)) <= threshold:
                    stroke.connection_points.pop(idx)
                    if len(stroke.connection_points) == 0:
                        self._convert_stroke_to_dynamic(stroke)
                    return True
        return False

    def _convert_stroke_to_dynamic(self, stroke: DrawnStroke) -> None:
        """Wandelt einen statisch verankerten Strich in ein dynamisches Physik-Objekt um."""
        if stroke.body:
            for s in stroke.segments + stroke.poly_shapes:
                if s in self.space.shapes:
                    self.space.remove(s)
                if s in self._level_static_shapes:
                    self._level_static_shapes.remove(s)
            if stroke.body in self.space.bodies:
                self.space.remove(stroke.body)

        com, mass, moment, local_segs, is_closed, local_polys = self._compute_stroke_physics(stroke.points)
        body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
        body.position = (com.x, com.y)
        segments = []
        polys = []

        if is_closed and local_polys:
            for piece in local_polys:
                poly = pymunk.Poly(body, piece)
                poly.elasticity = 0.25
                poly.friction = 0.75
                poly.collision_type = CTYPE_DRAWN
                polys.append(poly)
            self.space.add(body, *polys)
        else:
            for p1_local, p2_local in local_segs:
                seg = pymunk.Segment(body, p1_local, p2_local, SEGMENT_RADIUS)
                seg.elasticity = 0.35
                seg.friction = 0.7
                seg.collision_type = CTYPE_DRAWN
                segments.append(seg)
            self.space.add(body, *segments)

        stroke.body = body
        stroke.segments = segments
        stroke.poly_shapes = polys
        stroke.is_static = False
        stroke.is_closed = is_closed

    def remove_drawn_strokes(self) -> None:
        """Entfernt alle vom Spieler gezeichneten Linien."""
        for stroke in self.drawn_strokes:
            if stroke.body:
                for s in stroke.segments + stroke.poly_shapes:
                    if s in self.space.shapes:
                        self.space.remove(s)
                    if s in self._level_static_shapes:
                        self._level_static_shapes.remove(s)
                if stroke.body in self.space.bodies:
                    self.space.remove(stroke.body)
        self.drawn_strokes.clear()

    def remove_all_dynamic(self) -> None:
        """Entfernt alle dynamischen Objekte (Bälle, Säulen, Kästen) für Reset."""
        for ball in self.balls:
            if ball.shape in self.space.shapes:
                self.space.remove(ball.shape)
            if ball.body in self.space.bodies:
                self.space.remove(ball.body)
        self.balls.clear()

        for dbox in self.dynamic_boxes:
            if dbox.shape in self.space.shapes:
                self.space.remove(dbox.shape)
            if dbox.body in self.space.bodies:
                self.space.remove(dbox.body)
        self.dynamic_boxes.clear()

        self._balls_in_bucket.clear()
        self.balls_collided = False

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

    def draw(self, surface: pygame.Surface, hovered_conn_point: Optional[tuple[float, float]] = None) -> None:
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

        # Gezeichnete Striche & Blöcke
        for stroke in self.drawn_strokes:
            if stroke.is_closed and stroke.poly_shapes:
                for poly in stroke.poly_shapes:
                    verts = [poly.body.local_to_world(v) for v in poly.get_vertices()]
                    pts = [(int(v.x), int(v.y)) for v in verts]
                    if len(pts) >= 3:
                        pygame.draw.polygon(surface, stroke.color, pts)
                        border_col = tuple(max(0, c - 35) for c in stroke.color)
                        pygame.draw.polygon(surface, border_col, pts, 3)

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

            # Wenn statisch: Sichtbare metallische Verbindungspunkte (Niete) an allen Kontaktstellen mit Oberflächen
            if stroke.is_static and stroke.connection_points:
                for cx, cy in stroke.connection_points:
                    icx, icy = int(cx), int(cy)
                    is_hovered = (
                        hovered_conn_point is not None
                        and pymunk.Vec2d(icx, icy).get_distance(pymunk.Vec2d(*hovered_conn_point)) < 6.0
                    )
                    if is_hovered:
                        # Leuchtender orange-roter Warnring (Signal: Klick löst den Punkt)
                        pygame.draw.circle(surface, (235, 75, 60), (icx, icy), SEGMENT_RADIUS + 8, 3)
                        pygame.draw.circle(surface, (255, 230, 220), (icx, icy), SEGMENT_RADIUS + 4)
                        pygame.draw.circle(surface, (200, 60, 50), (icx, icy), SEGMENT_RADIUS + 1)
                        # Kleines weißes X
                        pygame.draw.line(surface, (255, 255, 255), (icx - 4, icy - 4), (icx + 4, icy + 4), 2)
                        pygame.draw.line(surface, (255, 255, 255), (icx - 4, icy + 4), (icx + 4, icy - 4), 2)
                    else:
                        # Äußerer dunkler Ring
                        pygame.draw.circle(surface, (45, 40, 35), (icx, icy), SEGMENT_RADIUS + 5)
                        # Heller Metall-Ring
                        pygame.draw.circle(surface, (230, 225, 215), (icx, icy), SEGMENT_RADIUS + 3)
                        # Nietkopf
                        pygame.draw.circle(surface, (115, 105, 95), (icx, icy), SEGMENT_RADIUS)
                        # Glanzpunkt
                        pygame.draw.circle(surface, (255, 255, 255), (icx - 1, icy - 1), 2)

        # Dynamische Kästen / Säulen
        for dbox in self.dynamic_boxes:
            verts = [dbox.body.local_to_world(v) for v in dbox.shape.get_vertices()]
            pts = [(int(v.x), int(v.y)) for v in verts]
            pygame.draw.polygon(surface, dbox.color, pts)
            border_col = tuple(max(0, c - 40) for c in dbox.color)
            pygame.draw.polygon(surface, border_col, pts, 2)

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
            self._level_static_shapes.append(seg)

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

    def _on_ball_collide_ball(
        self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: dict
    ) -> bool:
        self.balls_collided = True
        return True
