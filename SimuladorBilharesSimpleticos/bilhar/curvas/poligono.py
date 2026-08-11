"""
Polígono regular centrado na origem.

Parâmetros:
    a → número de lados (n >= 3). Usamos o parâmetro 'a' da UI.
    b → raio do círculo circunscrito (distância centro → vértice).
"""

from __future__ import annotations
import numpy as np
from bilhar.core.curva import CurvaBase


class Poligono(CurvaBase):
    def __init__(self, a: float = 4.0, b: float = 1.0):
        self.n = max(3, int(round(a)))          # número de lados
        self.raio = max(float(b), 1e-6)          # raio circunscrito

        # Ângulo interno entre vértices
        self.dtheta = 2 * np.pi / self.n

        # Vértices (sentido anti-horário, começando no eixo x positivo)
        self.vertices = np.array([
            [self.raio * np.cos(i * self.dtheta),
             self.raio * np.sin(i * self.dtheta)]
            for i in range(self.n)
        ])

        # Comprimento de cada lado
        self.len_lado = np.linalg.norm(self.vertices[1] - self.vertices[0])
        self.perimetro = self.n * self.len_lado

    def _s_from_t(self, t: float) -> float:
        t = t % (2 * np.pi)
        return (t / (2 * np.pi)) * self.perimetro

    def _t_from_s(self, s: float) -> float:
        s = s % self.perimetro
        return (s / self.perimetro) * 2 * np.pi

    def _segmento(self, s: float) -> tuple[int, float]:
        """Retorna (índice do lado, distância local ao longo do lado)."""
        s = s % self.perimetro
        i = int(s // self.len_lado) % self.n
        local = s - i * self.len_lado
        return i, local

    def ponto(self, t: float) -> np.ndarray:
        s = self._s_from_t(t)
        i, local = self._segmento(s)
        v0 = self.vertices[i]
        v1 = self.vertices[(i + 1) % self.n]
        direcao = v1 - v0
        return v0 + (local / self.len_lado) * direcao

    def tangente(self, t: float) -> np.ndarray:
        s = self._s_from_t(t)
        i, _ = self._segmento(s)
        v0 = self.vertices[i]
        v1 = self.vertices[(i + 1) % self.n]
        d = v1 - v0
        norma = np.linalg.norm(d)
        if norma < 1e-12:
            return np.array([1.0, 0.0])
        return d / norma

    def normal(self, t: float) -> np.ndarray:
        """Normal apontando para dentro do polígono."""
        tg = self.tangente(t)
        n = np.array([tg[1], -tg[0]])  # rotação -90°
        # Garante que aponta para o centro
        p = self.ponto(t)
        if np.dot(n, p) > 0:
            n = -n
        return n

    def intersect_line(self, point: np.ndarray, direction: np.ndarray) -> list[float]:
        """Interseção da reta com todos os lados do polígono."""
        px, py = point
        dx, dy = direction
        hits = []

        for i in range(self.n):
            v0 = self.vertices[i]
            v1 = self.vertices[(i + 1) % self.n]
            # Segmento: v0 + μ (v1 - v0), μ ∈ [0, 1]
            # Reta:    point + λ direction
            # Resolve o sistema 2x2
            sx, sy = v1 - v0
            denom = dx * sy - dy * sx
            if abs(denom) < 1e-14:
                continue  # paralelo

            # λ e μ
            lam = ((v0[0] - px) * sy - (v0[1] - py) * sx) / denom
            mu  = ((v0[0] - px) * dy - (v0[1] - py) * dx) / denom

            if 0.0 - 1e-8 <= mu <= 1.0 + 1e-8:
                hits.append(lam)

        return hits

    def t_from_pos(self, pos: np.ndarray) -> float:
        """Encontra o lado mais próximo e o parâmetro t correspondente."""
        x, y = float(pos[0]), float(pos[1])
        melhor_dist = np.inf
        melhor_s = 0.0

        for i in range(self.n):
            v0 = self.vertices[i]
            v1 = self.vertices[(i + 1) % self.n]
            d = v1 - v0
            len2 = np.dot(d, d)
            if len2 < 1e-14:
                continue
            mu = np.clip(np.dot(pos - v0, d) / len2, 0.0, 1.0)
            proj = v0 + mu * d
            dist = np.linalg.norm(pos - proj)
            if dist < melhor_dist:
                melhor_dist = dist
                melhor_s = i * self.len_lado + mu * self.len_lado

        return self._t_from_s(melhor_s)

    def sample(self, n: int = 10000) -> np.ndarray:
        # Amostra uniforme em comprimento de arco
        ts = np.linspace(0, 2 * np.pi, n, endpoint=False)
        pts = np.array([self.ponto(t) for t in ts])
        return pts.T