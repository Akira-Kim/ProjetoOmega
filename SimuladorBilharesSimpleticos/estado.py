"""Estado da simulação: tudo que descreve 'onde a bolinha está agora'."""
import numpy as np

from .curva import CurvaParametrica


class EstadoBilhar:
    def __init__(self):
        self.pausado = True
        self.primeiro_inicio = True
        self.modo_bilhar = 'Elástico'

        self.pos = np.array([1.0, 0.0])
        self.t = 0.0
        self.vel = np.array([-1.0, 1.0]) / np.sqrt(2)
        self.angulo_vel = 0.25 * np.pi
        self.velocidade_simulacao = 1.0

        self.curva_parametrica = CurvaParametrica()
        self.curve_points = None

        self.traj_x = [self.pos[0]]
        self.traj_y = [self.pos[1]]
        self.trajetoria_aux_x = []
        self.trajetoria_aux_y = []

        self.lista_t_colisao = []
        self.lista_angulo_colisao = []
        self.cos_angulo = 0.0
        self.reset_all = False

        # NOTA (Fase 1): 'heatmap' guarda uma referência a um artista do
        # matplotlib (ax2.imshow(...)), o que é um vazamento de
        # responsabilidade — estado não deveria saber de matplotlib.
        # Mantido assim de propósito nesta etapa para não mudar
        # comportamento. Remover na Fase 2 (visualizacao/), quando o
        # heatmap passa a ser responsabilidade só da camada de plot.
        self.heatmap = None
        self.heatmap_bins = 120

    def reset(self):
        self.pausado = True
        self.primeiro_inicio = True
        self.pos = np.array([1.0, 0.0])
        self.t = 0.0
        self.vel = np.array([-1.0, 1.0]) / np.sqrt(2)
        self.angulo_vel = 0.25 * np.pi
        self.velocidade_simulacao = 1.0
        self.curva_parametrica = CurvaParametrica()
        self.curve_points = None

        self.traj_x = [self.pos[0]]
        self.traj_y = [self.pos[1]]
        self.trajetoria_aux_x = []
        self.trajetoria_aux_y = []

        self.lista_t_colisao = []
        self.lista_angulo_colisao = []
        self.cos_angulo = 0.0

        if self.heatmap is not None:
            self.heatmap.set_data(np.zeros((self.heatmap_bins, self.heatmap_bins)))
            self.heatmap.set_clim(0, 1)

        self.reset_all = False
