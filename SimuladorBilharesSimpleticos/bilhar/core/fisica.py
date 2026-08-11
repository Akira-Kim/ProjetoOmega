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
    Implementação da colisão simplética usada no projeto original.

    Retorna:
        nova_velocidade,
        trajetoria_aux_x (para visualização da corda),
        trajetoria_aux_y
    """
    # Ponto anterior na curva (aproximação usando t_anterior)
    x_pos = curva.ponto(t_anterior)

    T = curva.tangente(t_hit)
    lambdas_sym = curva.intersect_line(x_pos, T)

    other_lambda = 0.0
    for lam in lambdas_sym:
        if abs(lam) > 1e-6:
            other_lambda = lam
            break

    z_pos = x_pos + other_lambda * T

    if np.linalg.norm(z_pos - hit_pos) < 1e-8:
        # Caso degenerado: cai para reflexão elástica
        n = curva.normal(t_hit)
        nova_vel = refletir_vetor(vel, n)
        traj_aux_x, traj_aux_y = [], []
    else:
        nova_vel = z_pos - hit_pos
        norma = np.linalg.norm(nova_vel)
        if norma > 1e-12:
            nova_vel = nova_vel / norma
        traj_aux_x = [x_pos[0], z_pos[0]]
        traj_aux_y = [x_pos[1], z_pos[1]]

    return nova_vel, traj_aux_x, traj_aux_y


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
