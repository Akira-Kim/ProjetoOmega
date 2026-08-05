"""Funções de física pura, sem dependência de matplotlib."""
import numpy as np


def refletir_vetor(v, n):
    """Reflete o vetor v em relação à normal n (reflexão especular)."""
    return v - 2 * np.dot(v, n) * n
