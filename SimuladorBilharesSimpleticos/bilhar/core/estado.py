"""
Estado completo da simulação.
Objeto puro, serializável e independente de gráficos.
"""

from __future__ import annotations
import numpy as np
from typing import Optional
from .curva import CurvaBase


def _criar_curva(nome: str, **params):
    """Import lazy para evitar import circular com bilhar.curvas."""
    from bilhar.curvas import criar_curva
    return criar_curva(nome, **params)


class EstadoSimulacao:
    def __init__(
        self,
        curva_nome: str = "Círculo",
        a: float = 1.0,
        b: float = 1.0,
        t0: float = 0.0,
        angulo_vel: float = 0.25 * np.pi,
        velocidade_simulacao: float = 1.0,
        modo: str = "Elástico",
    ):
        self.pausado: bool = True
        self.primeiro_inicio: bool = True
        self.modo_bilhar: str = modo

        self.curva: CurvaBase = _criar_curva(curva_nome, a=a, b=b)
        self.curva_nome: str = curva_nome
        self.parametro_a: float = a
        self.parametro_b: float = b

        # Evita começar exatamente em canto do Estádio (t=0 é junção)
        if curva_nome == "Estádio" and abs(t0) < 1e-9:
            # Coloca no meio da reta superior
            perim = getattr(self.curva, "perimetro", 2 * np.pi)
            len_reta = getattr(self.curva, "len_reta", 2.0)
            t0 = (len_reta * 0.5 / perim) * 2 * np.pi

        # Evita começar exatamente em vértice do Polígono
        if curva_nome == "Polígono" and abs(t0) < 1e-9:
            # Coloca no meio do primeiro lado
            perim = getattr(self.curva, "perimetro", 2 * np.pi)
            len_lado = getattr(self.curva, "len_lado", 1.0)
            t0 = (len_lado * 0.5 / perim) * 2 * np.pi

        self.t: float = t0
        self.pos: np.ndarray = self.curva.ponto(self.t)
        self.angulo_vel: float = angulo_vel
        self.velocidade_simulacao: float = velocidade_simulacao

        # Velocidade inicial alinhada com a tangente + ângulo
        tg = self.curva.tangente(self.t)
        self.vel: np.ndarray = np.array([
            tg[0] * np.cos(self.angulo_vel) - tg[1] * np.sin(self.angulo_vel),
            tg[1] * np.cos(self.angulo_vel) + tg[0] * np.sin(self.angulo_vel),
        ])
        # Garante que a velocidade aponta para dentro da região
        n_in = self.curva.normal(self.t)  # já é a normal interna
        if np.dot(self.vel, n_in) < 0:
            # Reflete o ângulo para o lado de dentro
            self.vel = self.vel - 2 * np.dot(self.vel, n_in) * n_in
            norma = np.linalg.norm(self.vel)
            if norma > 1e-12:
                self.vel /= norma

        # Históricos
        self.traj_x: list[float] = [self.pos[0]]
        self.traj_y: list[float] = [self.pos[1]]
        self.trajetoria_aux_x: list[float] = []
        self.trajetoria_aux_y: list[float] = []

        self.lista_t_colisao: list[float] = []
        self.lista_angulo_colisao: list[float] = []
        self.cos_angulo: float = 0.0

        # Heatmap (mantido no estado para facilitar atualização)
        self.heatmap_bins: int = 120
        self.heatmap_data: Optional[np.ndarray] = None  # preenchido pela viz

        self.reset_all: bool = False

    def reset(
        self,
        curva_nome: Optional[str] = None,
        a: Optional[float] = None,
        b: Optional[float] = None,
        t0: float = 0.0,
        angulo_vel: float = 0.25 * np.pi,
        velocidade_simulacao: float = 1.0,
        modo: Optional[str] = None,
    ):
        """Reinicia o estado (mantém curva/modo se não especificados)."""
        if curva_nome is None:
            curva_nome = self.curva_nome
        if a is None:
            a = self.parametro_a
        if b is None:
            b = self.parametro_b
        if modo is None:
            modo = self.modo_bilhar

        self.__init__(
            curva_nome=curva_nome,
            a=a,
            b=b,
            t0=t0,
            angulo_vel=angulo_vel,
            velocidade_simulacao=velocidade_simulacao,
            modo=modo,
        )

    def atualizar_curva(self, nome: str, a: float = 1.0, b: float = 1.0):
        """Troca a curva (só deve ser chamado antes de iniciar a simulação)."""
        if not self.primeiro_inicio:
            return
        self.curva = _criar_curva(nome, a=a, b=b)
        self.curva_nome = nome
        self.parametro_a = a
        self.parametro_b = b
        self.pos = self.curva.ponto(self.t)
        self._recalcular_velocidade()

    def _recalcular_velocidade(self):
        tg = self.curva.tangente(self.t)
        self.vel = np.array([
            tg[0] * np.cos(self.angulo_vel) - tg[1] * np.sin(self.angulo_vel),
            tg[1] * np.cos(self.angulo_vel) + tg[0] * np.sin(self.angulo_vel),
        ])
        # Garante direção para dentro
        n_in = self.curva.normal(self.t)
        if np.dot(self.vel, n_in) < 0:
            self.vel = self.vel - 2 * np.dot(self.vel, n_in) * n_in
            norma = np.linalg.norm(self.vel)
            if norma > 1e-12:
                self.vel /= norma

    def set_t(self, t: float):
        if self.primeiro_inicio:
            self.t = t
            self.pos = self.curva.ponto(self.t)
            self._recalcular_velocidade()
            self.traj_x = [self.pos[0]]
            self.traj_y = [self.pos[1]]

    def set_angulo(self, angulo: float):
        if self.primeiro_inicio:
            self.angulo_vel = angulo
            self._recalcular_velocidade()

    def set_velocidade_simulacao(self, vel: float):
        if self.primeiro_inicio:
            self.velocidade_simulacao = vel

    def set_modo(self, modo: str):
        if self.primeiro_inicio:
            self.modo_bilhar = modo
