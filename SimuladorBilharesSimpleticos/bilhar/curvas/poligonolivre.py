"""
Polígono livre – fronteira definida por vértices arbitrários.

- Recebe uma lista de pontos [[x1,y1], [x2,y2], ...]
- Fecha sozinho se o primeiro e o último forem diferentes
- Implementa CurvaBase (mesma interface das outras curvas)

Parâmetros a e b da UI são ignorados (a forma vem dos vértices).
"""

from __future__ import annotations
import numpy as np
from bilhar.core.curva import CurvaBase


class PoligonoLivre(CurvaBase):
    def __init__(self, vertices=None, a: float = 1.0, b: float = 1.0):
        # a e b ignorados (compatibilidade com a factory)
        if vertices is None:
            # Quadrado padrão (fallback)
            vertices = [
                [1.0, 1.0],
                [-1.0, 1.0],
                [-1.0, -1.0],
                [1.0, -1.0],
            ]

        verts = [np.asarray(v, dtype=float) for v in vertices]
        if len(verts) < 3:
            raise ValueError("PoligonoLivre precisa de pelo menos 3 vértices")

        # Fecha se necessário
        if not np.allclose(verts[0], verts[-1]):
            verts.append(verts[0].copy())

        self.vertices = np.array(verts)          # inclui o fechamento
        self.n_lados = len(self.vertices) - 1    # último = primeiro

        # Comprimentos dos lados
        self.lens = np.array([
            np.linalg.norm(self.vertices[i + 1] - self.vertices[i])
            for i in range(self.n_lados)
        ])
        self.perimetro = float(np.sum(self.lens))
        if self.perimetro < 1e-12:
            raise ValueError("Perímetro do polígono é zero")

    def _s_from_t(self, t: float) -> float:
        t = t % (2 * np.pi)
        return (t / (2 * np.pi)) * self.perimetro

    def _t_from_s(self, s: float) -> float:
        s = s % self.perimetro
        return (s / self.perimetro) * 2 * np.pi

    def _segmento(self, s: float) -> tuple[int, float]:
        """Retorna (índice do lado, distância local ao longo do lado)."""
        s = s % self.perimetro
        acum = 0.0
        for i in range(self.n_lados):
            if acum + self.lens[i] >= s - 1e-12:
                return i, s - acum
            acum += self.lens[i]
        return self.n_lados - 1, self.lens[-1]

    def ponto(self, t: float) -> np.ndarray:
        s = self._s_from_t(t)
        i, local = self._segmento(s)
        v0 = self.vertices[i]
        v1 = self.vertices[i + 1]
        if self.lens[i] < 1e-12:
            return v0.copy()
        return v0 + (local / self.lens[i]) * (v1 - v0)

    def tangente(self, t: float) -> np.ndarray:
        s = self._s_from_t(t)
        i, _ = self._segmento(s)
        d = self.vertices[i + 1] - self.vertices[i]
        norma = np.linalg.norm(d)
        if norma < 1e-12:
            return np.array([1.0, 0.0])
        return d / norma

    def normal(self, t: float) -> np.ndarray:
        """Normal apontando para dentro."""
        tg = self.tangente(t)
        n = np.array([tg[1], -tg[0]])  # rotação -90°
        p = self.ponto(t)
        # centro aproximado
        centro = np.mean(self.vertices[:-1], axis=0)
        if np.dot(n, p - centro) > 0:
            n = -n
        return n

    def intersect_line(self, point: np.ndarray, direction: np.ndarray) -> list[float]:
        px, py = float(point[0]), float(point[1])
        dx, dy = float(direction[0]), float(direction[1])
        hits = []

        for i in range(self.n_lados):
            v0 = self.vertices[i]
            v1 = self.vertices[i + 1]
            sx, sy = v1[0] - v0[0], v1[1] - v0[1]
            denom = dx * sy - dy * sx
            if abs(denom) < 1e-14:
                continue

            lam = ((v0[0] - px) * sy - (v0[1] - py) * sx) / denom
            mu = ((v0[0] - px) * dy - (v0[1] - py) * dx) / denom

            if -1e-8 <= mu <= 1.0 + 1e-8:
                hits.append(lam)

        return hits

    def t_from_pos(self, pos: np.ndarray) -> float:
        pos = np.asarray(pos, dtype=float)
        melhor_dist = np.inf
        melhor_s = 0.0

        for i in range(self.n_lados):
            v0 = self.vertices[i]
            v1 = self.vertices[i + 1]
            d = v1 - v0
            len2 = np.dot(d, d)
            if len2 < 1e-14:
                continue
            mu = np.clip(np.dot(pos - v0, d) / len2, 0.0, 1.0)
            proj = v0 + mu * d
            dist = np.linalg.norm(pos - proj)
            if dist < melhor_dist:
                melhor_dist = dist
                melhor_s = float(np.sum(self.lens[:i]) + mu * self.lens[i])

        return self._t_from_s(melhor_s)

    def sample(self, n: int = 10000) -> np.ndarray:
        ts = np.linspace(0, 2 * np.pi, n, endpoint=False)
        pts = np.array([self.ponto(t) for t in ts])
        return pts.T