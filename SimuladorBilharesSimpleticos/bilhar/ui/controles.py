"""
Controles de interface usando widgets do Matplotlib (Fase 1).
Na Fase 3 estes controles devem migrar para PySide6 ou Dear PyGui.
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox, RadioButtons
from matplotlib import patches
from matplotlib.figure import Figure

from bilhar.core.estado import EstadoSimulacao
from bilhar.viz.canvas import CanvasConfiguracao
from bilhar.viz.fase import CanvasFase
from bilhar.viz.animacao import AnimacaoBilhar


class ControlesUI:
    def __init__(
        self,
        fig: Figure,
        estado: EstadoSimulacao,
        canvas_config: CanvasConfiguracao,
        canvas_fase: CanvasFase,
        animacao: AnimacaoBilhar,
    ):
        self.fig = fig
        self.estado = estado
        self.canvas_config = canvas_config
        self.canvas_fase = canvas_fase
        self.animacao = animacao

        self._criar_widgets()
        self._conectar_callbacks()

    def _criar_widgets(self):
        # --- Fronteira ---
        self.fig.patches.append(
            patches.Rectangle(
                (0.05, 0.15), 0.15, 0.07,
                transform=self.fig.transFigure,
                facecolor="#f0f0f5", edgecolor="#cccccc", alpha=0.7,
            )
        )
        ax_radio = plt.axes([0.05, 0.05, 0.13, 0.12])
        self.radio = RadioButtons(ax_radio, ["Círculo", "Elipse", "Estádio"], active=0)
        self.fig.text(0.095, 0.18, "Fronteira", transform=self.fig.transFigure, ha="center", fontsize=9)

        # --- Parâmetros a, b ---
        self.fig.patches.append(
            patches.Rectangle(
                (0.25, 0.15), 0.20, 0.07,
                transform=self.fig.transFigure,
                facecolor="#f0f0f5", edgecolor="#cccccc", alpha=0.7,
            )
        )
        self.fig.text(0.25, 0.18, "Parâmetros da Curva", transform=self.fig.transFigure, ha="center", fontsize=9)
        ax_texto_a = plt.axes([0.24, 0.14, 0.06, 0.04])
        self.texto_a = TextBox(ax_texto_a, "a", initial="1.0")
        ax_texto_b = plt.axes([0.24, 0.10, 0.06, 0.04])
        self.texto_b = TextBox(ax_texto_b, "b", initial="1.0")

        # --- Modo de colisão ---
        self.fig.patches.append(
            patches.Rectangle(
                (0.35, 0.15), 0.15, 0.07,
                transform=self.fig.transFigure,
                facecolor="#f0f0f5", edgecolor="#cccccc", alpha=0.7,
            )
        )
        ax_radio_modo = plt.axes([0.34, 0.07, 0.13, 0.1])
        self.radio_modo = RadioButtons(ax_radio_modo, ["Elástico", "Simplético"], active=0)
        self.fig.text(0.385, 0.18, "Colisão", transform=self.fig.transFigure, ha="center", fontsize=9)

        # --- Condição inicial ---
        self.fig.text(0.65, 0.18, "Condição Inicial", transform=self.fig.transFigure, ha="center", fontsize=9)
        ax_pos_t = plt.axes([0.60, 0.15, 0.15, 0.02])
        self.slider_pos_t = Slider(ax_pos_t, "t (× π)", 0, 2, valinit=0, valstep=0.005)
        ax_angulo = plt.axes([0.60, 0.11, 0.15, 0.02])
        self.slider_angulo = Slider(ax_angulo, "Ângulo (× π)", 0, 1, valinit=0.25, valstep=0.01)
        ax_vel = plt.axes([0.60, 0.07, 0.15, 0.02])
        self.slider_vel = Slider(ax_vel, "Velocidade", 0.5, 4.0, valinit=1.0, valstep=0.1)

        # --- Botões de controle ---
        self.fig.patches.append(
            patches.Rectangle(
                (0.50, 0.05), 0.48, 0.09,
                transform=self.fig.transFigure,
                facecolor="#f0f0f5", edgecolor="#cccccc", alpha=0.7,
            )
        )
        self.fig.text(0.86, 0.18, "Controles da Simulação", transform=self.fig.transFigure, ha="center", fontsize=9)

        ax_botao_start = plt.axes([0.82, 0.13, 0.08, 0.04])
        self.botao_start_pause = Button(ax_botao_start, "Iniciar", color="#ddffdd")
        ax_botao_reset = plt.axes([0.82, 0.08, 0.08, 0.04])
        self.botao_reset = Button(ax_botao_reset, "Reset", color="#ffdddd")
        ax_botao_info = plt.axes([0.82, 0.03, 0.08, 0.04])
        self.botao_info = Button(ax_botao_info, "Info", color="#ddddff")

    def _conectar_callbacks(self):
        self.radio.on_clicked(self._on_curva)
        self.radio_modo.on_clicked(self._on_modo)
        self.texto_a.on_submit(self._on_parametros)
        self.texto_b.on_submit(self._on_parametros)
        self.slider_pos_t.on_changed(self._on_pos_t)
        self.slider_angulo.on_changed(self._on_angulo)
        self.slider_vel.on_changed(self._on_vel)
        self.botao_start_pause.on_clicked(self._on_start_pause)
        self.botao_reset.on_clicked(self._on_reset)
        self.botao_info.on_clicked(self._on_info)

    # ---------- Callbacks ----------

    def _on_curva(self, label):
        if self.estado.primeiro_inicio:
            a = float(self.texto_a.text)
            b = float(self.texto_b.text)
            self.estado.atualizar_curva(label, a=a, b=b)
            self.canvas_config.atualizar_estado_inicial(self.estado)
            self.fig.canvas.draw_idle()

    def _on_modo(self, label):
        if self.estado.primeiro_inicio:
            self.estado.set_modo(label)
            self.canvas_config.texto_info.set_text(
                f"Curva: {self.estado.curva_nome} | Modo: {self.estado.modo_bilhar}"
            )
            self.fig.canvas.draw_idle()

    def _on_parametros(self, _=None):
        if self.estado.primeiro_inicio:
            try:
                a = float(self.texto_a.text)
                b = float(self.texto_b.text)
                self.estado.atualizar_curva(self.estado.curva_nome, a=a, b=b)
                self.canvas_config.atualizar_estado_inicial(self.estado)
                self.fig.canvas.draw_idle()
            except ValueError:
                pass

    def _on_pos_t(self, val):
        if self.estado.primeiro_inicio:
            self.estado.set_t(val * np.pi)
            self.canvas_config.atualizar_estado_inicial(self.estado)
            self.fig.canvas.draw_idle()

    def _on_angulo(self, val):
        if self.estado.primeiro_inicio:
            self.estado.set_angulo(val * np.pi)
            self.canvas_config.atualizar_estado_inicial(self.estado)
            self.fig.canvas.draw_idle()

    def _on_vel(self, val):
        if self.estado.primeiro_inicio:
            self.estado.set_velocidade_simulacao(val)

    def _on_start_pause(self, event):
        if self.estado.pausado:
            self.estado.pausado = False
            self.canvas_config.texto_info.set_text("Simulação em andamento...")
            self.botao_start_pause.label.set_text("Pausar")
            self.botao_reset.label.set_text("Reset")
            self.estado.reset_all = False
            self.animacao.iniciar()
        else:
            self.estado.pausado = True
            self.canvas_config.texto_info.set_text("Simulação pausada")
            self.botao_start_pause.label.set_text("Continuar")

    def _on_reset(self, event):
        self.slider_pos_t.set_val(0)
        self.slider_angulo.set_val(0.25)
        self.slider_vel.set_val(1.0)
        self.texto_a.set_val("1.0")
        self.texto_b.set_val("1.0")
        self.botao_start_pause.label.set_text("Iniciar")
        self.canvas_config.texto_info.set_text("Pronto para iniciar")

        self.estado.reset()
        self.canvas_fase.reset_heatmap(self.estado)
        self.canvas_config.atualizar_estado_inicial(self.estado)
        self.canvas_fase.atualizar(self.estado)

        if self.estado.reset_all:
            self.botao_reset.label.set_text("Reset")
            self.estado.reset_all = False
        else:
            self.estado.reset_all = True
            self.botao_reset.label.set_text("Reset all")

        self.fig.canvas.draw_idle()

    def _on_info(self, event):
        self.canvas_config.texto_info.set_text(
            "Simulação de Bilhares – Versão Modular (Fase 1)\n"
            "• Física separada da visualização\n"
            "• Curvas plugáveis (Círculo / Elipse)\n"
            "• Mapa de calor inferno + nearest\n"
            "• Pronto para expansão (Fase 2+)"
        )
        self.fig.canvas.draw_idle()
