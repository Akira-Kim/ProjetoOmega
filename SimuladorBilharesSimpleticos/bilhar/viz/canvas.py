"""
Canvas do espaço de configuração (curva + bola + trajetória).
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from bilhar.core.estado import EstadoSimulacao


class CanvasConfiguracao:
    def __init__(self, ax: Axes):
        self.ax = ax
        self.ax.set_facecolor("#fafafa")
        self.ax.set_aspect("equal")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title("Espaço de Configuração", pad=20, fontsize=14, color="#333333")

        self.curva_plot, = ax.plot([], [], "k-", linewidth=2, alpha=0.8)
        self.bolinha, = ax.plot([], [], "ro", markersize=6, zorder=3)
        self.trajeto, = ax.plot([], [], "r-", linewidth=1.2, alpha=0.75)
        self.trajeto_aux, = ax.plot([], [], "c--", linewidth=1.8, alpha=0.85)
        self.normal_linha, = ax.plot([], [], "b--", linewidth=1.5, alpha=0.6)
        self.vel_linha, = ax.plot([], [], "g-", linewidth=1.5, alpha=0.8)
        self.tangente_linha, = ax.plot([], [], "m-", linewidth=1.5, alpha=0.6)

        self.texto_info = ax.text(
            0.02, 0.95, "",
            transform=ax.transAxes,
            fontsize=10,
            bbox=dict(facecolor="white", alpha=0.95, edgecolor="#cccccc"),
        )

    def atualizar_curva(self, estado: EstadoSimulacao):
        pts = estado.curva.sample(10000)
        self.curva_plot.set_data(pts[0], pts[1])

        margin = 0.6
        self.ax.set_xlim(np.min(pts[0]) - margin, np.max(pts[0]) + margin)
        self.ax.set_ylim(np.min(pts[1]) - margin, np.max(pts[1]) + margin)

    def atualizar_estado_inicial(self, estado: EstadoSimulacao):
        """Atualiza bola, tangente e velocidade no modo de preparação."""
        self.atualizar_curva(estado)

        pos = estado.pos
        tg = estado.curva.tangente(estado.t)
        self.tangente_linha.set_data(
            [pos[0], pos[0] + tg[0]],
            [pos[1], pos[1] + tg[1]],
        )
        self.vel_linha.set_data(
            [pos[0], pos[0] + estado.vel[0]],
            [pos[1], pos[1] + estado.vel[1]],
        )
        self.bolinha.set_data([pos[0]], [pos[1]])
        self.trajeto.set_data(estado.traj_x, estado.traj_y)
        self.trajeto_aux.set_data([], [])
        self.normal_linha.set_data([], [])

        self.texto_info.set_text(
            f"Curva: {estado.curva_nome} | Modo: {estado.modo_bilhar}"
        )

    def atualizar_frame(self, estado: EstadoSimulacao):
        """Atualização durante a animação."""
        self.bolinha.set_data([estado.pos[0]], [estado.pos[1]])
        self.trajeto.set_data(estado.traj_x, estado.traj_y)
        self.trajeto_aux.set_data(estado.trajetoria_aux_x, estado.trajetoria_aux_y)

    def limpar_auxiliares(self):
        self.normal_linha.set_data([], [])
        self.vel_linha.set_data([], [])
        self.tangente_linha.set_data([], [])
        self.trajeto_aux.set_data([], [])
