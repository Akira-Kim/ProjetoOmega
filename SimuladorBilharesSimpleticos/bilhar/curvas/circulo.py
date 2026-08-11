"""
Círculo unitário.
"""

import numpy as np
from bilhar.core.curva import CurvaBase


class Circulo(CurvaBase):
    def __init__(self, a: float = 1.0, b: float = 1.0):
        # a e b são ignorados (mantidos por compatibilidade com a factory)
        self.raio = 1.0

    def ponto(self, t: float) -> np.ndarray:
        return np.array([np.cos(t), np.sin(t)])

    def tangente(self, t: float) -> np.ndarray:
        return np.array([-np.sin(t), np.cos(t)])

    def intersect_line(self, point: np.ndarray, direction: np.ndarray) -> list[float]:
        """Interseção reta × círculo unitário."""
        px, py = point
        dx, dy = direction

        A = dx**2 + dy**2
        B = 2 * (px * dx + py * dy)
        C = px**2 + py**2 - 1.0

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
        t = np.arctan2(pos[1], pos[0])
        return t if t >= 0 else t + 2 * np.pi
