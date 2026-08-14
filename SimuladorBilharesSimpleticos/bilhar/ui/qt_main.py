"""
Janela principal PySide6
- Desenho poligonal / mão livre
- Fronteira por fórmula polar r(θ)
"""

from __future__ import annotations
import sys
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QDoubleSpinBox, QGroupBox, QFormLayout,
    QLabel, QLineEdit
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
from bilhar.curvas.poligonolivre import PoligonoLivre
from bilhar.curvas.parametrica import curva_de_formula_polar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Bilhares Simpléticos – Fase 3 (PySide6)")
        self.resize(1400, 900)

        self.estado = EstadoSimulacao(curva_nome="Círculo", a=1.0, b=1.0, modo="Elástico")
        self.integrador = Integrador(self.estado)

        self.modo_desenho = None
        self.vertices_desenho = []
        self.arrastando = False
        self.plot_vertices = None
        self.plot_arestas = None

        self.fig = Figure(figsize=(12, 8), facecolor="#f0f0f5")
        gs = gridspec.GridSpec(1, 2, width_ratios=[1.6, 1.0], wspace=0.28)
        self.ax_config = self.fig.add_subplot(gs[0])
        self.ax_fase = self.fig.add_subplot(gs[1])

        self.canvas_config = CanvasConfiguracao(self.ax_config)
        self.canvas_fase = CanvasFase(self.ax_fase)
        self.canvas_fase.garantir_heatmap(self.estado)

        self.mpl_canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.mpl_canvas, self)

        self.mpl_canvas.mpl_connect("button_press_event", self._on_press)
        self.mpl_canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.mpl_canvas.mpl_connect("button_release_event", self._on_release)

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)

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
        right.addWidget(self._criar_grupo_desenho())
        right.addWidget(self._criar_grupo_formula())
        right.addWidget(self._criar_grupo_botoes())
        right.addStretch()
        main_layout.addLayout(right, stretch=1)

        self.canvas_config.atualizar_estado_inicial(self.estado)
        self.canvas_fase.atualizar(self.estado)
        self.canvas_config.texto_info.set_text("Pronto para iniciar")
        self.mpl_canvas.draw()

    def _tick(self):
        if self.estado.pausado or self.modo_desenho:
            return
        dt = 0.012 * self.estado.velocidade_simulacao
        self.integrador.passo(dt)
        self.canvas_config.atualizar_frame(self.estado)
        self.canvas_fase.atualizar(self.estado)
        self.mpl_canvas.draw_idle()

    # ---------- grupos ----------
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

    def _criar_grupo_desenho(self) -> QGroupBox:
        box = QGroupBox("Desenho de fronteira")
        layout = QVBoxLayout(box)
        self.btn_poligonal = QPushButton("Desenhar polígono")
        self.btn_poligonal.clicked.connect(self._on_iniciar_poligonal)
        layout.addWidget(self.btn_poligonal)
        self.btn_mao = QPushButton("Desenhar à mão")
        self.btn_mao.clicked.connect(self._on_iniciar_mao_livre)
        layout.addWidget(self.btn_mao)
        self.btn_fechar = QPushButton("Fechar forma")
        self.btn_fechar.clicked.connect(self._on_fechar)
        self.btn_fechar.setEnabled(False)
        layout.addWidget(self.btn_fechar)
        self.btn_limpar = QPushButton("Limpar desenho")
        self.btn_limpar.clicked.connect(self._on_limpar_desenho)
        layout.addWidget(self.btn_limpar)
        self.lbl_desenho = QLabel("Pontos: 0")
        layout.addWidget(self.lbl_desenho)
        return box

    def _criar_grupo_formula(self) -> QGroupBox:
        box = QGroupBox("Fórmula polar r(θ)")
        layout = QVBoxLayout(box)
        self.edit_formula = QLineEdit("1 + 0.3*cos(3*theta)")
        self.edit_formula.setPlaceholderText("ex: 1 + 0.3*cos(3*theta)")
        layout.addWidget(self.edit_formula)
        self.btn_gerar = QPushButton("Gerar curva")
        self.btn_gerar.clicked.connect(self._on_gerar_formula)
        layout.addWidget(self.btn_gerar)
        hint = QLabel("Use: theta, sin, cos, tan, pi, sqrt...")
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(hint)
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

    # ---------- fórmula ----------
    def _on_gerar_formula(self):
        formula = self.edit_formula.text().strip()
        if not formula:
            self.canvas_config.texto_info.set_text("Digite uma fórmula r(θ).")
            self.mpl_canvas.draw_idle()
            return
        try:
            curva = curva_de_formula_polar(formula, n_pontos=400)
        except Exception as e:
            self.canvas_config.texto_info.set_text(f"Erro na fórmula: {e}")
            self.mpl_canvas.draw_idle()
            return

        self._aplicar_curva_livre(curva, f"Fórmula aplicada: {formula}")

    def _aplicar_curva_livre(self, curva: PoligonoLivre, msg: str):
        self.timer.stop()
        self.estado.pausado = True
        self.btn_start.setText("Iniciar")

        self.estado.curva = curva
        self.estado.curva_nome = "Polígono Livre"
        self.estado.primeiro_inicio = True
        self.estado.lista_t_colisao.clear()
        self.estado.lista_angulo_colisao.clear()

        perim = curva.perimetro
        t0 = (curva.lens[0] * 0.5 / perim) * 2 * np.pi
        self.estado.t = t0
        self.estado.pos = curva.ponto(t0)
        self.estado._recalcular_velocidade()
        self.estado.traj_x = [float(self.estado.pos[0])]
        self.estado.traj_y = [float(self.estado.pos[1])]

        self.modo_desenho = None
        self.arrastando = False
        self.vertices_desenho = []
        self.btn_fechar.setEnabled(False)
        self.btn_poligonal.setText("Desenhar polígono")
        self.btn_mao.setText("Desenhar à mão")
        self.combo_curva.setCurrentText("Polígono Livre")

        self.canvas_fase.reset_heatmap(self.estado)
        self.canvas_config.atualizar_estado_inicial(self.estado)
        self.canvas_fase.atualizar(self.estado)
        self.canvas_config.texto_info.set_text(msg)
        self._atualizar_preview()
        self.mpl_canvas.draw()

    # ---------- desenho ----------
    def _entrar_modo_desenho(self, tipo: str, msg: str):
        self.timer.stop()
        self.estado.pausado = True
        self.btn_start.setText("Iniciar")
        self.modo_desenho = tipo
        self.vertices_desenho = []
        self.arrastando = False
        self.btn_fechar.setEnabled(True)
        self.lbl_desenho.setText("Pontos: 0")
        self.canvas_config.texto_info.set_text(msg)
        self._atualizar_preview()
        self.mpl_canvas.draw()

    def _on_iniciar_poligonal(self):
        self._entrar_modo_desenho(
            "poligonal",
            "Poligonal: clique para adicionar vértices. Mínimo 3. Depois Fechar."
        )
        self.btn_poligonal.setText("Desenhando polígono...")
        self.btn_mao.setText("Desenhar à mão")

    def _on_iniciar_mao_livre(self):
        self._entrar_modo_desenho(
            "mao_livre",
            "Mão livre: clique e arraste. Solte e clique Fechar."
        )
        self.btn_mao.setText("Desenhando à mão...")
        self.btn_poligonal.setText("Desenhar polígono")

    def _on_press(self, event):
        if not self.modo_desenho:
            return
        if event.inaxes != self.ax_config or event.button != 1:
            return
        if event.xdata is None or event.ydata is None:
            return
        pt = [float(event.xdata), float(event.ydata)]
        if self.modo_desenho == "poligonal":
            self.vertices_desenho.append(pt)
            self.lbl_desenho.setText(f"Pontos: {len(self.vertices_desenho)}")
            self._atualizar_preview()
            self.mpl_canvas.draw_idle()
        elif self.modo_desenho == "mao_livre":
            self.arrastando = True
            self.vertices_desenho = [pt]
            self.lbl_desenho.setText("Pontos: 1")
            self._atualizar_preview()
            self.mpl_canvas.draw_idle()

    def _on_motion(self, event):
        if self.modo_desenho != "mao_livre" or not self.arrastando:
            return
        if event.inaxes != self.ax_config:
            return
        if event.xdata is None or event.ydata is None:
            return
        pt = [float(event.xdata), float(event.ydata)]
        if self.vertices_desenho:
            last = self.vertices_desenho[-1]
            if (pt[0] - last[0]) ** 2 + (pt[1] - last[1]) ** 2 < 1e-4:
                return
        self.vertices_desenho.append(pt)
        self.lbl_desenho.setText(f"Pontos: {len(self.vertices_desenho)}")
        self._atualizar_preview()
        self.mpl_canvas.draw_idle()

    def _on_release(self, event):
        if self.modo_desenho == "mao_livre":
            self.arrastando = False

    def _atualizar_preview(self):
        if self.plot_vertices is not None:
            try:
                self.plot_vertices.remove()
            except Exception:
                pass
            self.plot_vertices = None
        if self.plot_arestas is not None:
            try:
                self.plot_arestas.remove()
            except Exception:
                pass
            self.plot_arestas = None
        if not self.vertices_desenho:
            return
        xs = [v[0] for v in self.vertices_desenho]
        ys = [v[1] for v in self.vertices_desenho]
        estilo = "o" if self.modo_desenho == "poligonal" else "."
        tam = 7 if self.modo_desenho == "poligonal" else 3
        self.plot_vertices, = self.ax_config.plot(
            xs, ys, estilo, color="#2980b9", markersize=tam, zorder=20
        )
        if len(self.vertices_desenho) >= 2:
            self.plot_arestas, = self.ax_config.plot(
                xs, ys, "-", color="#3498db", linewidth=1.6, alpha=0.9, zorder=19
            )

    def _simplificar(self, pontos, eps=0.02):
        if len(pontos) < 3:
            return pontos
        pts = np.asarray(pontos, dtype=float)

        def _rdp(pts, eps):
            if len(pts) < 3:
                return pts
            inicio, fim = pts[0], pts[-1]
            d = fim - inicio
            leng = np.linalg.norm(d)
            if leng < 1e-12:
                dists = np.linalg.norm(pts - inicio, axis=1)
            else:
                u = d / leng
                proj = np.dot(pts - inicio, u)
                closest = inicio + np.outer(proj, u)
                dists = np.linalg.norm(pts - closest, axis=1)
            i = int(np.argmax(dists))
            if dists[i] > eps:
                left = _rdp(pts[: i + 1], eps)
                right = _rdp(pts[i:], eps)
                return np.vstack([left[:-1], right])
            return np.vstack([inicio, fim])

        return _rdp(pts, eps).tolist()

    def _on_fechar(self):
        pts = self.vertices_desenho
        if self.modo_desenho == "mao_livre" and len(pts) > 40:
            pts = self._simplificar(pts, eps=0.025)
        if len(pts) < 3:
            self.canvas_config.texto_info.set_text("Precisa de pelo menos 3 pontos.")
            self.mpl_canvas.draw_idle()
            return
        curva = PoligonoLivre(vertices=pts)
        self._aplicar_curva_livre(curva, f"Forma fechada com {curva.n_lados} lados.")

    def _on_limpar_desenho(self):
        self.vertices_desenho = []
        self.modo_desenho = None
        self.arrastando = False
        self.btn_fechar.setEnabled(False)
        self.btn_poligonal.setText("Desenhar polígono")
        self.btn_mao.setText("Desenhar à mão")
        self.lbl_desenho.setText("Pontos: 0")
        self._atualizar_preview()
        self.canvas_config.texto_info.set_text("Desenho limpo.")
        self.mpl_canvas.draw_idle()

    # ---------- callbacks gerais ----------
    def _on_curva(self, nome: str):
        if self.estado.primeiro_inicio and not self.modo_desenho:
            self.estado.atualizar_curva(nome, a=self.spin_a.value(), b=self.spin_b.value())
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
        if self.estado.primeiro_inicio and not self.modo_desenho:
            self.estado.atualizar_curva(
                self.estado.curva_nome, a=self.spin_a.value(), b=self.spin_b.value()
            )
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
        if self.modo_desenho:
            self.canvas_config.texto_info.set_text("Feche a forma antes de iniciar.")
            self.mpl_canvas.draw_idle()
            return
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
        if self.modo_desenho:
            return
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
        self.modo_desenho = None
        self.arrastando = False
        self.vertices_desenho = []
        self.btn_fechar.setEnabled(False)
        self.btn_poligonal.setText("Desenhar polígono")
        self.btn_mao.setText("Desenhar à mão")
        self.lbl_desenho.setText("Pontos: 0")
        self._atualizar_preview()
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
        self.canvas_config.texto_info.set_text("Pronto para iniciar")
        self.mpl_canvas.draw()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()