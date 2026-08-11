"""
Leis de colisão e utilitários físicos.
Independente de visualização.
"""

import numpy as np
from .curva import CurvaBase


def refletir_vetor(v: np.ndarray, n: np.ndarray) -> np.ndarray:
    """Reflexão elástica clássica: v' = v - 2 (v·n) n."""
    return v - 2 * np.dot(v, n) * n


def aplicar_colisao_elastica(vel: np.ndarray, normal: np.ndarray) -> np.ndarray:
    """Aplica reflexão elástica e normaliza (opcional, mas mantém |v|)."""
    nova_vel = refletir_vetor(vel, normal)
    norma = np.linalg.norm(nova_vel)
    if norma > 1e-12:
        return nova_vel / norma * np.linalg.norm(vel)  # preserva velocidade
    return nova_vel


def aplicar_colisao_simpletica(
    curva: CurvaBase,
    t_hit: float,
    hit_pos: np.ndarray,
    vel: np.ndarray,
    t_anterior: float,
) -> tuple[np.ndarray, list, list]:
    """
    Colisão simplética com verificação de validade.
    Se a construção gerar ponto fora da fronteira ou velocidade ruim,
    cai automaticamente para reflexão elástica.
    """
    def _fallback():
        n = curva.normal(t_hit)
        nova_vel = refletir_vetor(vel, n)
        norma = np.linalg.norm(nova_vel)
        if norma > 1e-12:
            nova_vel /= norma
        return nova_vel, [], []

    try:
        x_pos = curva.ponto(t_anterior)
        T = curva.tangente(t_hit)

        lambdas_sym = curva.intersect_line(x_pos, T)

        other_lambda = 0.0
        for lam in lambdas_sym:
            if abs(lam) > 1e-5:
                other_lambda = lam
                break

        if abs(other_lambda) < 1e-5:
            return _fallback()

        z_pos = x_pos + other_lambda * T

        # 1. z_pos não pode ficar quase em cima do hit
        if np.linalg.norm(z_pos - hit_pos) < 1e-6:
            return _fallback()

        # 2. z_pos precisa estar próximo da curva
        t_z = curva.t_from_pos(z_pos)
        z_proj = curva.ponto(t_z)
        if np.linalg.norm(z_pos - z_proj) > 1e-3:
            return _fallback()

        nova_vel = z_pos - hit_pos
        norma = np.linalg.norm(nova_vel)
        if norma < 1e-10:
            return _fallback()

        nova_vel /= norma

        # 3. deve apontar para dentro
        n_in = curva.normal(t_hit)
        if np.dot(nova_vel, n_in) < 0:
            return _fallback()

        traj_aux_x = [float(x_pos[0]), float(z_pos[0])]
        traj_aux_y = [float(x_pos[1]), float(z_pos[1])]
        return nova_vel, traj_aux_x, traj_aux_y

    except Exception:
        return _fallback()


def aplicar_colisao(
    modo: str,
    curva: CurvaBase,
    t_hit: float,
    hit_pos: np.ndarray,
    vel: np.ndarray,
    t_anterior: float,
) -> tuple[np.ndarray, list, list]:
    """
    Despacha para a lei de colisão correta.

    Retorna (nova_vel, traj_aux_x, traj_aux_y)
    """
    if modo == "Elástico":
        n = curva.normal(t_hit)
        nova_vel = refletir_vetor(vel, n)
        # Normaliza para manter velocidade unitária (como no original)
        norma = np.linalg.norm(nova_vel)
        if norma > 1e-12:
            nova_vel /= norma
        return nova_vel, [], []
    else:  # Simplético
        return aplicar_colisao_simpletica(curva, t_hit, hit_pos, vel, t_anterior)
