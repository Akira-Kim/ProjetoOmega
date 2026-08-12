"""
Janela principal em PySide6 (Fase 3).
Animação dirigida por QTimer (mais estável que FuncAnimation dentro do Qt).
"""

from __future__ import annotations
import sys
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QDoubleSpinBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import QTimer

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import gridspec

from bilhar.core.estado import EstadoSimulacao
from bilhar.viz.canvas import CanvasConfiguracao
from bilhar.viz.fase import CanvasFase
from bilhar.core.integrador import Integrador
from bilhar.curvas import listar_curvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Bilhares Simpléticos – Fase 3 (PySide6)")
        self.resize(1400, 900)

        # ---------- Estado e física ----------
        self.estado = EstadoSimulacao(
            curva_nome="Círculo",
            a=1.0, b=1.0,
            modo="Elástico",
        )
        self.integrador = Integrador(self.estado)

        # ---------- Figura Matplotlib ----------
        self.fig = Figure(figsize=(12, 8), facecolor="#f0f0f5")
        gs = gridspec.GridSpec(1, 2, width_ratios=[1.6, 1.0], wspace=0.28)
        self.ax_config = self.fig.add_subplot(gs[0])
        self.ax_fase = self.fig.add_subplot(gs[1])

        self.canvas_config = CanvasConfiguracao(self.ax_config)
        self.canvas_fase = CanvasFase(self.ax_fase)
        self.canvas_fase.garantir_heatmap(self.estado)

        self.mpl_canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.mpl_canvas, self)

        # ---------- Timer de animação (Qt) ----------
        self.timer = QTimer(self)
        self.timer.setInterval(16)  # ~60 FPS
        self.timer.timeout.connect(self._tick)

        # ---------- Layout Qt ----------
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        left = QVBoxLayout()
        left.addWidget(self.toolbar)
        left.addWidget(self.mpl_canvas)
        main_layout.addLayout(left, stretch=4)

        right = QVBoxLayout()
        right.addWidget(self._criar_grupo_curva())
        right.addWidget(self._criar_grupo_modo())
        right.addWidget(self._criar_grupo_parametros())
        right.addWidget(self._criar_grupo_condicao_inicial())
        right.addWidget(self._criar_grupo_botoes())
        right.addStretch()
        main_layout.addLayout(right, stretch=1)

        # Desenho inicial
        self.canvas_config.atualizar_estado_inicial(self.estado)
        self.canvas_fase.atualizar(self.estado)
        self.canvas_config.texto_info.set_text("Pronto para iniciar (PySide6 + QTimer)")
        self.mpl_canvas.draw()

    # ------------------------------------------------------------------
    # Loop de animação
    # ------------------------------------------------------------------
    def _tick(self):
        """Chamado pelo QTimer a cada frame."""
        if self.estado.pausado:
            return

        dt = 0.012 * self.estado.velocidade_simulacao
        self.integrador.passo(dt)

        self.canvas_config.atualizar_frame(self.estado)
        self.canvas_fase.atualizar(self.estado)
        self.mpl_canvas.draw_idle()

    # ------------------------------------------------------------------
    # Grupos de controles
    # ------------------------------------------------------------------
    def _criar_grupo_curva(self) -> QGroupBox:
        box = QGroupBox("Fronteira")
        layout = QVBoxLayout(box)
        self.combo_curva = QComboBox()
        self.combo_curva.addItems(listar_curvas())
        self.combo_curva.currentTextChanged.connect(self._on_curva)
        layout.addWidget(self.combo_curva)
        return box

    def _criar_grupo_modo(self) -> QGroupBox:
        box = QGroupBox("Colisão")
        layout = QVBoxLayout(box)
        self.combo_modo = QComboBox()
        self.combo_modo.addItems(["Elástico", "Simplético"])
        self.combo_modo.currentTextChanged.connect(self._on_modo)
        layout.addWidget(self.combo_modo)
        return box

    def _criar_grupo_parametros(self) -> QGroupBox:
        box = QGroupBox("Parâmetros")
        layout = QFormLayout(box)

        self.spin_a = QDoubleSpinBox()
        self.spin_a.setRange(0.1, 20.0)
        self.spin_a.setValue(1.0)
        self.spin_a.setSingleStep(0.1)
        self.spin_a.valueChanged.connect(self._on_parametros)

        self.spin_b = QDoubleSpinBox()
        self.spin_b.setRange(0.1, 20.0)
        self.spin_b.setValue(1.0)
        self.spin_b.setSingleStep(0.1)
        self.spin_b.valueChanged.connect(self._on_parametros)

        layout.addRow("a", self.spin_a)
        layout.addRow("b", self.spin_b)
        return box

    def _criar_grupo_condicao_inicial(self) -> QGroupBox:
        box = QGroupBox("Condição Inicial")
        layout = QFormLayout(box)

        self.spin_t = QDoubleSpinBox()
        self.spin_t.setRange(0.0, 2.0)
        self.spin_t.setValue(0.0)
        self.spin_t.setSingleStep(0.01)
        self.spin_t.setDecimals(3)
        self.spin_t.valueChanged.connect(self._on_t)
        layout.addRow("t (× π)", self.spin_t)

        self.spin_angulo = QDoubleSpinBox()
        self.spin_angulo.setRange(0.0, 1.0)
        self.spin_angulo.setValue(0.25)
        self.spin_angulo.setSingleStep(0.01)
        self.spin_angulo.setDecimals(3)
        self.spin_angulo.valueChanged.connect(self._on_angulo)
        layout.addRow("Ângulo (× π)", self.spin_angulo)

        self.spin_vel = QDoubleSpinBox()
        self.spin_vel.setRange(0.5, 4.0)
        self.spin_vel.setValue(1.0)
        self.spin_vel.setSingleStep(0.1)
        self.spin_vel.setDecimals(2)
        self.spin_vel.valueChanged.connect(self._on_vel)
        layout.addRow("Velocidade", self.spin_vel)

        return box

    def _criar_grupo_botoes(self) -> QGroupBox:
        box = QGroupBox("Simulação")
        layout = QVBoxLayout(box)

        self.btn_start = QPushButton("Iniciar")
        self.btn_start.clicked.connect(self._on_start_pause)
        layout.addWidget(self.btn_start)

        self.btn_step = QPushButton("Passo a passo")
        self.btn_step.clicked.connect(self._on_step)
        layout.addWidget(self.btn_step)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self._on_reset)
        layout.addWidget(self.btn_reset)

        return box

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _on_curva(self, nome: str):
        if self.estado.primeiro_inicio:
            a = self.spin_a.value()
            b = self.spin_b.value()
            self.estado.atualizar_curva(nome, a=a, b=b)
            self.canvas_config.atualizar_estado_inicial(self.estado)
            self.mpl_canvas.draw()

    def _on_modo(self, modo: str):
        if self.estado.primeiro_inicio:
            self.estado.set_modo(modo)
            self.canvas_config.texto_info.set_text(
                f"Curva: {self.estado.curva_nome} | Modo: {self.estado.modo_bilhar}"
            )
            self.mpl_canvas.draw()

    def _on_parametros(self):
        if self.estado.primeiro_inicio:
            a = self.spin_a.value()
            b = self.spin_b.value()
            self.estado.atualizar_curva(self.estado.curva_nome, a=a, b=b)
            self.canvas_config.atualizar_estado_inicial(self.estado)
            self.mpl_canvas.draw()

    def _on_t(self, val: float):
        if self.estado.primeiro_inicio:
            self.estado.set_t(val * np.pi)
            self.canvas_config.atualizar_estado_inicial(self.estado)
            self.mpl_canvas.draw()

    def _on_angulo(self, val: float):
        if self.estado.primeiro_inicio:
            self.estado.set_angulo(val * np.pi)
            self.canvas_config.atualizar_estado_inicial(self.estado)
            self.mpl_canvas.draw()

    def _on_vel(self, val: float):
        if self.estado.primeiro_inicio:
            self.estado.set_velocidade_simulacao(val)

    def _on_start_pause(self):
        if self.estado.pausado:
            self.estado.pausado = False
            self.estado.primeiro_inicio = False
            self.btn_start.setText("Pausar")
            self.canvas_config.texto_info.set_text("Simulação em andamento...")
            self.timer.start()
        else:
            self.estado.pausado = True
            self.btn_start.setText("Continuar")
            self.canvas_config.texto_info.set_text("Simulação pausada")
            self.timer.stop()
        self.mpl_canvas.draw()

    def _on_step(self):
        self.timer.stop()
        self.estado.pausado = False
        self.estado.primeiro_inicio = False

        n_antes = len(self.estado.lista_t_colisao)
        for _ in range(500):
            self.integrador.passo(0.02)
            if len(self.estado.lista_t_colisao) > n_antes:
                break

        self.estado.pausado = True
        self.btn_start.setText("Continuar")

        self.canvas_config.atualizar_frame(self.estado)
        self.canvas_fase.atualizar(self.estado)
        self.canvas_config.texto_info.set_text(
            f"Passo a passo | Colisões: {len(self.estado.lista_t_colisao)}"
        )
        self.mpl_canvas.draw()

    def _on_reset(self):
        self.timer.stop()
        self.estado.reset()
        self.spin_a.setValue(1.0)
        self.spin_b.setValue(1.0)
        self.spin_t.setValue(0.0)
        self.spin_angulo.setValue(0.25)
        self.spin_vel.setValue(1.0)
        self.combo_curva.setCurrentIndex(0)
        self.combo_modo.setCurrentIndex(0)
        self.btn_start.setText("Iniciar")
        self.canvas_fase.reset_heatmap(self.estado)
        self.canvas_config.atualizar_estado_inicial(self.estado)
        self.canvas_fase.atualizar(self.estado)
        self.canvas_config.texto_info.set_text("Pronto para iniciar (PySide6 + QTimer)")
        self.mpl_canvas.draw()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()