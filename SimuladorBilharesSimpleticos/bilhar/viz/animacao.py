"""
Gerencia a FuncAnimation do Matplotlib.
"""

from __future__ import annotations
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from bilhar.core.estado import EstadoSimulacao
from bilhar.core.integrador import Integrador
from bilhar.viz.canvas import CanvasConfiguracao
from bilhar.viz.fase import CanvasFase


class AnimacaoBilhar:
    def __init__(
        self,
        fig: Figure,
        estado: EstadoSimulacao,
        canvas_config: CanvasConfiguracao,
        canvas_fase: CanvasFase,
        interval: int = 10,
    ):
        self.fig = fig
        self.estado = estado
        self.canvas_config = canvas_config
        self.canvas_fase = canvas_fase
        self.integrador = Integrador(estado)
        self.interval = interval
        self.ani: FuncAnimation | None = None

    def init_anim(self):
        return (
            self.canvas_config.curva_plot,
            self.canvas_config.bolinha,
            self.canvas_config.trajeto,
            self.canvas_config.trajeto_aux,
            self.canvas_config.normal_linha,
            self.canvas_config.vel_linha,
            self.canvas_config.tangente_linha,
            self.canvas_fase.colisao_plot,
            self.canvas_config.texto_info,
        )

    def update(self, frame):
        if self.estado.pausado:
            return self.init_anim()

        dt = 0.012 * self.estado.velocidade_simulacao
        self.integrador.passo(dt)

        self.canvas_config.atualizar_frame(self.estado)
        self.canvas_fase.atualizar(self.estado)

        return self.init_anim()

    def iniciar(self):
        if self.estado.primeiro_inicio:
            self.estado.primeiro_inicio = False

        if self.ani is not None:
            self.ani.event_source.stop()

        self.ani = FuncAnimation(
            self.fig,
            self.update,
            frames=None,
            init_func=self.init_anim,
            blit=False,
            interval=self.interval,
            cache_frame_data=False,
        )
        self.fig.canvas.draw()

    def parar(self):
        if self.ani is not None:
            self.ani.event_source.stop()
