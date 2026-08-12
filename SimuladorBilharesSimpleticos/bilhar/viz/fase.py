"""
Canvas do espaço de fase + mapa de calor
- Eixos adaptativos (focam na região onde há dados)
- Heatmap mais legível (vazios claros, dados em magma)
"""

from __future__ import annotations
import numpy as np
from matplotlib.axes import Axes
from bilhar.core.estado import EstadoSimulacao


class CanvasFase:
    def __init__(self, ax: Axes):
        self.ax = ax
        self.ax.set_facecolor("#f7f7f7")
        self.ax.grid(True, alpha=0.35, linestyle="--", color="#888888")
        self.ax.set_title("Espaço de Fase + Mapa de Calor", pad=12, fontsize=13, color="#222222")
        self.ax.set_xlabel("Parâmetro t (× π)", fontsize=10, color="#333333")
        self.ax.set_ylabel("cos θ (ângulo com a tangente)", fontsize=10, color="#333333")

        # Limites iniciais (domínio teórico completo)
        self.ax.set_xlim(0, 2)
        self.ax.set_ylim(-1, 1)
        self.ax.tick_params(colors="#333333", labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color("#555555")

        # Pontos de colisão
        self.colisao_plot, = ax.plot(
            [], [],
            "o",
            markersize=4.0,
            markerfacecolor="#e74c3c",
            markeredgecolor="#1a1a1a",
            markeredgewidth=0.35,
            alpha=0.92,
            linestyle="None",
            zorder=10,
        )

        self.heatmap = None
        self._colorbar = None

    def garantir_heatmap(self, estado: EstadoSimulacao):
        if self._colorbar is not None:
            try:
                self._colorbar.remove()
            except Exception:
                pass
            self._colorbar = None

        if self.heatmap is not None:
            try:
                self.heatmap.remove()
            except Exception:
                pass
            self.heatmap = None

        # Começa com NaN para que células vazias fiquem transparentes
        initial = np.full((estado.heatmap_bins, estado.heatmap_bins), np.nan)

        self.heatmap = self.ax.imshow(
            initial,
            origin="lower",
            extent=[0, 2, -1, 1],
            cmap="magma",
            aspect="auto",
            alpha=0.88,
            interpolation="bilinear",
            zorder=1,
            vmin=0,
            vmax=1,
        )
        # Células NaN ficam transparentes (mostra o fundo claro)
        self.heatmap.cmap.set_bad(color="#f7f7f7", alpha=0.0)

        self.colisao_plot.set_zorder(10)

        self._colorbar = self.ax.figure.colorbar(
            self.heatmap,
            ax=self.ax,
            pad=0.02,
            fraction=0.046,
        )
        self._colorbar.set_label("log(1 + colisões)", fontsize=9, color="#333333")
        self._colorbar.ax.yaxis.set_tick_params(color="#333333", labelcolor="#333333")

    def _adaptar_eixos(self, estado: EstadoSimulacao):
        """Ajusta xlim/ylim para a região onde existem colisões (com margem)."""
        n = len(estado.lista_t_colisao)
        if n < 8:
            # Poucos pontos: mantém domínio teórico
            self.ax.set_xlim(0, 2)
            self.ax.set_ylim(-1, 1)
            return

        xs = np.asarray(estado.lista_t_colisao)
        ys = np.asarray(estado.lista_angulo_colisao)

        x_min, x_max = float(np.min(xs)), float(np.max(xs))
        y_min, y_max = float(np.min(ys)), float(np.max(ys))

        # Margem proporcional (mínimo garantido)
        x_margin = max(0.08, 0.12 * (x_max - x_min + 1e-6))
        y_margin = max(0.06, 0.15 * (y_max - y_min + 1e-6))

        self.ax.set_xlim(
            max(0.0, x_min - x_margin),
            min(2.0, x_max + x_margin),
        )
        self.ax.set_ylim(
            max(-1.0, y_min - y_margin),
            min(1.0, y_max + y_margin),
        )

    def atualizar(self, estado: EstadoSimulacao):
        self.colisao_plot.set_data(
            estado.lista_t_colisao,
            estado.lista_angulo_colisao,
        )

        n = len(estado.lista_t_colisao)
        if n <= 5:
            return

        # Eixos adaptativos
        self._adaptar_eixos(estado)

        if self.heatmap is None or n % 2 != 0:
            return

        hist, _, _ = np.histogram2d(
            estado.lista_t_colisao,
            estado.lista_angulo_colisao,
            bins=estado.heatmap_bins,
            range=[[0, 2], [-1, 1]],
        )
        log_hist = np.log1p(hist)

        # Zeros → NaN (ficam transparentes)
        log_hist = np.where(log_hist > 0, log_hist, np.nan)

        self.heatmap.set_data(log_hist.T)

        # Escala de cor só com valores reais
        valid = log_hist[np.isfinite(log_hist)]
        if valid.size > 0:
            vmax = float(np.max(valid))
            self.heatmap.set_clim(0, max(vmax * 1.08, 0.5))
        else:
            self.heatmap.set_clim(0, 1)

    def reset_heatmap(self, estado: EstadoSimulacao):
        if self.heatmap is not None:
            empty = np.full((estado.heatmap_bins, estado.heatmap_bins), np.nan)
            self.heatmap.set_data(empty)
            self.heatmap.set_clim(0, 1)
        self.colisao_plot.set_data([], [])
        self.ax.set_xlim(0, 2)
        self.ax.set_ylim(-1, 1)