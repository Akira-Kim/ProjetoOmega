"""
Estádio de Bunimovich (stadium billiard).

Geometria:
- Dois segmentos paralelos de comprimento 2*a (parte reta)
- Duas semicircunferências de raio r nas extremidades

Parâmetros:
    a : semi-comprimento da parte reta (a >= 0)
    r : raio das tampas circulares (r > 0)  →  usamos o parâmetro 'b' da UI como r

A parametrização usa o comprimento de arco normalizado para o intervalo [0, 2π),
para manter compatibilidade com o espaço de fase existente (t / π).
"""

from __future__ import annotations
import numpy as np
from bilhar.core.curva import CurvaBase


class Estadio(CurvaBase):
    def __init__(self, a: float = 1.0, b: float = 1.0):
        """
        a = semi-comprimento da parte reta
        b = raio das semicircunferências (r)
        """
        self.a = max(float(a), 0.0)
        self.r = max(float(b), 1e-6)

        # Comprimentos das partes
        self.len_reta = 2.0 * self.a
        self.len_semi = np.pi * self.r
        self.perimetro = 2.0 * self.len_reta + 2.0 * self.len_semi

    def _s_from_t(self, t: float) -> float:
        """Converte t ∈ [0, 2π) para comprimento de arco s ∈ [0, perimetro)."""
        t = t % (2 * np.pi)
        return (t / (2 * np.pi)) * self.perimetro

    def _t_from_s(self, s: float) -> float:
        s = s % self.perimetro
        return (s / self.perimetro) * 2 * np.pi

    def _segmento(self, s: float) -> tuple[int, float]:
        """
        Retorna (índice do segmento, parâmetro local).
        Segmentos:
            0: reta superior   (y = +r), x de -a → +a
            1: semi direita    centro (a, 0)
            2: reta inferior   (y = -r), x de +a → -a
            3: semi esquerda   centro (-a, 0)
        """
        s = s % self.perimetro
        if s < self.len_reta:
            return 0, s
        s -= self.len_reta
        if s < self.len_semi:
            return 1, s
        s -= self.len_semi
        if s < self.len_reta:
            return 2, s
        s -= self.len_reta
        return 3, s

    def ponto(self, t: float) -> np.ndarray:
        s = self._s_from_t(t)
        seg, local = self._segmento(s)

        if seg == 0:  # reta superior
            x = -self.a + local
            y = self.r
            return np.array([x, y])
        if seg == 1:  # semi direita
            theta = -np.pi / 2 + local / self.r   # de -π/2 a +π/2
            return np.array([self.a + self.r * np.cos(theta), self.r * np.sin(theta)])
        if seg == 2:  # reta inferior
            x = self.a - local
            y = -self.r
            return np.array([x, y])
        # seg == 3: semi esquerda
        theta = np.pi / 2 + local / self.r        # de +π/2 a +3π/2
        return np.array([-self.a + self.r * np.cos(theta), self.r * np.sin(theta)])

    def tangente(self, t: float) -> np.ndarray:
        s = self._s_from_t(t)
        seg, local = self._segmento(s)

        if seg == 0:
            return np.array([1.0, 0.0])
        if seg == 1:
            theta = -np.pi / 2 + local / self.r
            return np.array([-np.sin(theta), np.cos(theta)])
        if seg == 2:
            return np.array([-1.0, 0.0])
        # seg == 3
        theta = np.pi / 2 + local / self.r
        return np.array([-np.sin(theta), np.cos(theta)])

    def normal(self, t: float) -> np.ndarray:
        """Normal apontando para dentro do estádio."""
        tg = self.tangente(t)
        n = np.array([tg[1], -tg[0]])  # rotação -90°
        p = self.ponto(t)
        if np.dot(n, p) > 0:          # se aponta para fora, inverte
            n = -n
        return n

    def intersect_line(self, point: np.ndarray, direction: np.ndarray) -> list[float]:
        """
        Interseção da reta point + λ*direction com o estádio.
        Considera as 2 retas e as 2 semicircunferências.
        """
        px, py = point
        dx, dy = direction
        hits: list[float] = []

        # Retas horizontais y = ±r (só no intervalo x ∈ [-a, a])
        if abs(dy) > 1e-14:
            for y_reta in (self.r, -self.r):
                lam = (y_reta - py) / dy
                x = px + lam * dx
                if -self.a - 1e-8 <= x <= self.a + 1e-8:
                    hits.append(lam)

        # Semicírculos
        hits.extend(self._intersect_semicircle(point, direction, cx=self.a,  cy=0.0, lado="dir"))
        hits.extend(self._intersect_semicircle(point, direction, cx=-self.a, cy=0.0, lado="esq"))

        return hits

    def _intersect_semicircle(
        self, point: np.ndarray, direction: np.ndarray, cx: float, cy: float, lado: str
    ) -> list[float]:
        px, py = point
        dx, dy = direction
        fx = px - cx
        fy = py - cy
        A = dx * dx + dy * dy
        B = 2 * (fx * dx + fy * dy)
        C = fx * fx + fy * fy - self.r * self.r

        disc = B * B - 4 * A * C
        if disc < 0 or abs(A) < 1e-14:
            return []

        sd = np.sqrt(disc)
        lambs = [(-B + sd) / (2 * A), (-B - sd) / (2 * A)]
        valid = []
        for lam in lambs:
            x = px + lam * dx
            if lado == "dir" and x >= cx - 1e-8:
                valid.append(lam)
            elif lado == "esq" and x <= cx + 1e-8:
                valid.append(lam)
        return valid

    def t_from_pos(self, pos: np.ndarray) -> float:
        """Recupera o parâmetro t a partir de um ponto aproximadamente sobre a curva."""
        x, y = pos
        if abs(y - self.r) < 1e-5 and -self.a - 1e-5 <= x <= self.a + 1e-5:
            s = (x + self.a)
            return self._t_from_s(s)
        if abs(y + self.r) < 1e-5 and -self.a - 1e-5 <= x <= self.a + 1e-5:
            s = self.len_reta + self.len_semi + (self.a - x)
            return self._t_from_s(s)
        if x >= self.a - 1e-5:
            theta = np.arctan2(y, x - self.a)
            local = (theta + np.pi / 2) * self.r
            s = self.len_reta + local
            return self._t_from_s(s)
        # semi esquerda
        theta = np.arctan2(y, x + self.a)
        if theta < 0:
            theta += 2 * np.pi
        local = (theta - np.pi / 2) * self.r
        s = self.len_reta + self.len_semi + self.len_reta + local
        return self._t_from_s(s)

    def sample(self, n: int = 10000) -> np.ndarray:
        ts = np.linspace(0, 2 * np.pi, n, endpoint=True)
        pts = np.array([self.ponto(t) for t in ts]).T
        return pts