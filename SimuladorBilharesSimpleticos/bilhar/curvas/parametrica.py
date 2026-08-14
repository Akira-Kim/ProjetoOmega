"""
Curva a partir de fórmula polar r(θ).

Exemplo:
    r(θ) = 1 + 0.3*cos(3*θ)

Por enquanto: amostra a fórmula e devolve um PoligonoLivre.
"""

from __future__ import annotations
import numpy as np
from bilhar.curvas.poligonolivre import PoligonoLivre


# Funções permitidas na fórmula (seguro, sem eval aberto)
_ALLOWED = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "pi": np.pi,
    "exp": np.exp,
    "log": np.log,
}


def _avaliar_r(formula: str, theta: np.ndarray) -> np.ndarray:
    """
    Avalia r(θ) de forma restrita.
    A fórmula deve usar o nome 'theta' ou 't'.
    """
    expr = formula.strip()
    # aceita r(theta) = ... ou só a expressão
    if "=" in expr:
        expr = expr.split("=", 1)[1].strip()

    expr = expr.replace("θ", "theta")
    expr = expr.replace("θ", "theta")

    # troca t por theta se a pessoa escrever t
    # (evita confundir com tan)
    local = {"theta": theta, "t": theta, **_ALLOWED}

    try:
        r = eval(expr, {"__builtins__": {}}, local)
    except Exception as e:
        raise ValueError(f"Não foi possível interpretar a fórmula: {e}") from e

    r = np.asarray(r, dtype=float)
    if r.shape != theta.shape:
        r = np.broadcast_to(r, theta.shape).copy()
    if np.any(r <= 0):
        raise ValueError("r(θ) precisa ser > 0 em todo o intervalo")
    return r


def curva_de_formula_polar(
    formula: str,
    n_pontos: int = 400,
) -> PoligonoLivre:
    """
    Gera um PoligonoLivre a partir de r(θ).
    θ percorre [0, 2π).
    """
    theta = np.linspace(0, 2 * np.pi, n_pontos, endpoint=False)
    r = _avaliar_r(formula, theta)
    xs = r * np.cos(theta)
    ys = r * np.sin(theta)
    vertices = np.column_stack([xs, ys]).tolist()
    return PoligonoLivre(vertices=vertices)