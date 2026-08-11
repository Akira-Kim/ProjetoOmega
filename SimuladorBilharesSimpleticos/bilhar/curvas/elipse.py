"""
Elipse x = a cos(t), y = b sin(t).
"""

import numpy as np
from bilhar.core.curva import CurvaBase


class Elipse(CurvaBase):
    def __init__(self, a: float = 1.0, b: float = 1.0):
        self.a = float(a)
        self.b = float(b)

    def ponto(self, t: float) -> np.ndarray:
        return np.array([self.a * np.cos(t), self.b * np.sin(t)])

    def tangente(self, t: float) -> np.ndarray:
        d = np.array([-self.a * np.sin(t), self.b * np.cos(t)])
        norma = np.linalg.norm(d)
        if norma < 1e-12:
            return np.array([1.0, 0.0])
        return d / norma

    def intersect_line(self, point: np.ndarray, direction: np.ndarray) -> list[float]:
        """Interseção reta × elipse (escalada)."""
        aa, bb = self.a, self.b
        px, py = point
        dx, dy = direction

        A = (dx / aa) ** 2 + (dy / bb) ** 2
        B = 2 * (px * dx / aa**2 + py * dy / bb**2)
        C = (px / aa) ** 2 + (py / bb) ** 2 - 1.0

        disc = B**2 - 4 * A * C
        if disc < 0:
            return []
        if abs(A) < 1e-14:
            return [0.0] if abs(C) < 1e-14 else []

        sd = np.sqrt(disc)
        l1 = (-B + sd) / (2 * A)
        l2 = (-B - sd) / (2 * A)
        return [l1, l2]

    def t_from_pos(self, pos: np.ndarray) -> float:
        t = np.arctan2(pos[1] / self.b, pos[0] / self.a)
        return t if t >= 0 else t + 2 * np.pi
