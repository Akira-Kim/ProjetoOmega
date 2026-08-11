"""
Canvas do espaço de fase + mapa de calor.
"""

from __future__ import annotations
import numpy as np
from matplotlib.axes import Axes
from bilhar.core.estado import EstadoSimulacao


class CanvasFase:
    def __init__(self, ax: Axes):
        self.ax = ax
        self.ax.set_facecolor("#fafafa")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title("Espaço de Fase + Mapa de Calor (inferno)", pad=20, fontsize=14)
        self.ax.set_xlabel("Parâmetro t (× π)", fontsize=10)
        self.ax.set_ylabel("cos θ (ângulo com a tangente)", fontsize=10)
        self.ax.set_xlim(0, 2)
        self.ax.set_ylim(-1, 1)

        self.colisao_plot, = ax.plot([], [], "ro", markersize=3.5, alpha=0.98, zorder=10)

        self.heatmap = None
        self._colorbar = None

    def garantir_heatmap(self, estado: EstadoSimulacao):
        if self.heatmap is None:
            initial = np.zeros((estado.heatmap_bins, estado.heatmap_bins))
            self.heatmap = self.ax.imshow(
                initial,
                origin="lower",
                extent=[0, 2, -1, 1],
                cmap="inferno",
                aspect="auto",
                alpha=0.92,
                interpolation="nearest",
            )
            self.colisao_plot.set_zorder(10)
            self.heatmap.set_zorder(1)
            self._colorbar = self.ax.figure.colorbar(
                self.heatmap, ax=self.ax, pad=0.02,
                label="log(1 + nº de colisões por bin)",
            )

    def atualizar(self, estado: EstadoSimulacao):
        self.colisao_plot.set_data(estado.lista_t_colisao, estado.lista_angulo_colisao)

        # Atualiza heatmap periodicamente
        n = len(estado.lista_t_colisao)
        if n > 5 and n % 2 == 0:
            hist, _, _ = np.histogram2d(
                estado.lista_t_colisao,
                estado.lista_angulo_colisao,
                bins=estado.heatmap_bins,
                range=[[0, 2], [-1, 1]],
            )
            log_hist = np.log1p(hist)
            self.heatmap.set_data(log_hist.T)
            if np.max(log_hist) > 0:
                self.heatmap.set_clim(0, np.max(log_hist) * 1.05)

    def reset_heatmap(self, estado: EstadoSimulacao):
        if self.heatmap is not None:
            self.heatmap.set_data(np.zeros((estado.heatmap_bins, estado.heatmap_bins)))
            self.heatmap.set_clim(0, 1)
