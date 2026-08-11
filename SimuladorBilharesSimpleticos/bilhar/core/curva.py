"""
Interface base para curvas (fronteiras) do bilhar.
Toda nova curva deve herdar de CurvaBase e implementar os métodos abstratos.
"""

from abc import ABC, abstractmethod
import numpy as np


class CurvaBase(ABC):
    """Interface mínima que toda fronteira deve implementar."""

    @abstractmethod
    def ponto(self, t: float) -> np.ndarray:
        """
        Retorna a posição 2D [x, y] correspondente ao parâmetro t.
        t tipicamente em [0, 2π) para curvas fechadas.
        """
        pass

    @abstractmethod
    def tangente(self, t: float) -> np.ndarray:
        """Retorna o vetor tangente unitário no parâmetro t."""
        pass

    def normal(self, t: float) -> np.ndarray:
        """Normal unitária (rotação de 90° da tangente). Pode ser sobrescrito."""
        tg = self.tangente(t)
        return np.array([-tg[1], tg[0]])

    @abstractmethod
    def intersect_line(self, point: np.ndarray, direction: np.ndarray) -> list[float]:
        """
        Resolve a interseção da reta (point + λ * direction) com a curva.
        Retorna lista de valores de λ (pode conter negativos).
        """
        pass

    @abstractmethod
    def t_from_pos(self, pos: np.ndarray) -> float:
        """
        Dado um ponto aproximado na curva, retorna o parâmetro t correspondente.
        Preferencialmente em [0, 2π).
        """
        pass

    def sample(self, n: int = 10000) -> np.ndarray:
        """
        Amostra n pontos da curva para plotagem.
        Retorna array de shape (2, n) com [xs, ys].
        """
        ts = np.linspace(0, 2 * np.pi, n, endpoint=True)
        pts = np.array([self.ponto(t) for t in ts]).T
        return pts

    def __call__(self, t: float) -> np.ndarray:
        """Atalho: retorna [t, x, y] (compatibilidade com código legado)."""
        p = self.ponto(t)
        return np.array([t, p[0], p[1]])
