"""
animations.py — Easing-Funktionen und Animations-Hilfsmittel für py-brain-it-on.
"""
from __future__ import annotations

import math
import time


# ---------------------------------------------------------------------------
# Easing-Funktionen (t ∈ [0, 1] → [0, 1])
# ---------------------------------------------------------------------------

def ease_linear(t: float) -> float:
    return t


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    if t < 0.5:
        return 4 * t ** 3
    return 1 - (-2 * t + 2) ** 3 / 2


def ease_out_bounce(t: float) -> float:
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def ease_out_elastic(t: float) -> float:
    c4 = (2 * math.pi) / 3
    if t == 0:
        return 0
    if t == 1:
        return 1
    return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_in_back(t: float) -> float:
    c1, c3 = 1.70158, 1.70158 + 1
    return c3 * t * t * t - c1 * t * t


def ease_out_back(t: float) -> float:
    c1, c3 = 1.70158, 1.70158 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


# ---------------------------------------------------------------------------
# Interpolation
# ---------------------------------------------------------------------------

def lerp(a: float, b: float, t: float) -> float:
    """Lineare Interpolation."""
    return a + (b - a) * t


def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    """Interpoliert zwischen zwei RGB-Farben."""
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


# ---------------------------------------------------------------------------
# Tween-Klasse
# ---------------------------------------------------------------------------

class Tween:
    """Einfacher Tween für einen einzelnen Wert."""

    def __init__(
        self,
        start: float,
        end: float,
        duration: float,
        easing=ease_out_cubic,
        on_complete=None,
    ):
        self.start = start
        self.end = end
        self.duration = duration
        self.easing = easing
        self.on_complete = on_complete
        self._elapsed = 0.0
        self._done = False
        self.value = start

    @property
    def done(self) -> bool:
        return self._done

    def update(self, dt: float) -> float:
        if self._done:
            return self.value
        self._elapsed = min(self._elapsed + dt, self.duration)
        t = self._elapsed / self.duration if self.duration > 0 else 1.0
        self.value = lerp(self.start, self.end, self.easing(t))
        if self._elapsed >= self.duration:
            self._done = True
            self.value = self.end
            if self.on_complete:
                self.on_complete()
        return self.value

    def reset(self) -> None:
        self._elapsed = 0.0
        self._done = False
        self.value = self.start


class ShakeEffect:
    """Schütteleffekt für Objekte bei falscher Antwort."""

    def __init__(self, intensity: float = 8.0, duration: float = 0.5):
        self.intensity = intensity
        self.duration = duration
        self._elapsed = 0.0
        self.active = False
        self.offset_x = 0.0

    def start(self) -> None:
        self._elapsed = 0.0
        self.active = True

    def update(self, dt: float) -> float:
        if not self.active:
            self.offset_x = 0.0
            return 0.0
        self._elapsed += dt
        if self._elapsed >= self.duration:
            self.active = False
            self.offset_x = 0.0
            return 0.0
        progress = self._elapsed / self.duration
        decay = 1 - progress
        self.offset_x = math.sin(self._elapsed * 40) * self.intensity * decay
        return self.offset_x


class PulseEffect:
    """Pulsierender Skalierungseffekt."""

    def __init__(self, min_scale: float = 0.95, max_scale: float = 1.05, speed: float = 2.0):
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.speed = speed
        self._time = 0.0
        self.scale = 1.0

    def update(self, dt: float) -> float:
        self._time += dt
        t = (math.sin(self._time * self.speed * math.pi) + 1) / 2
        self.scale = lerp(self.min_scale, self.max_scale, t)
        return self.scale
