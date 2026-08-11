"""
Ponto de entrada do Simulador de Bilhares Simpléticos (versão modular – Fase 1).
"""

import matplotlib.pyplot as plt
from matplotlib import gridspec

from bilhar.core.estado import EstadoSimulacao
from bilhar.viz.canvas import CanvasConfiguracao
from bilhar.viz.fase import CanvasFase
from bilhar.viz.animacao import AnimacaoBilhar
from bilhar.ui.controles import ControlesUI


def main():
    plt.style.use("seaborn-v0_8")
    plt.rcParams["font.size"] = 10

    fig = plt.figure(figsize=(16, 12))
    fig.set_facecolor("#f0f0f5")

    gs_main = gridspec.GridSpec(2, 1, height_ratios=[8, 2], hspace=0.05)
    gs_graficos = gridspec.GridSpecFromSubplotSpec(
        1, 2, subplot_spec=gs_main[0], width_ratios=[2, 1]
    )

    ax = fig.add_subplot(gs_graficos[0])
    ax2 = fig.add_subplot(gs_graficos[1])

    # Eixo de controles (apenas para ocupar espaço; widgets são criados em coordenadas de figura)
    ax_controles = fig.add_subplot(gs_main[1])
    ax_controles.set_axis_off()

    # Estado inicial
    estado = EstadoSimulacao(
        curva_nome="Círculo",
        a=1.0,
        b=1.0,
        t0=0.0,
        angulo_vel=0.25 * 3.1415926535,
        velocidade_simulacao=1.0,
        modo="Elástico",
    )

    # Camadas de visualização
    canvas_config = CanvasConfiguracao(ax)
    canvas_fase = CanvasFase(ax2)
    canvas_fase.garantir_heatmap(estado)

    # Animação
    animacao = AnimacaoBilhar(fig, estado, canvas_config, canvas_fase)

    # Interface
    controles = ControlesUI(fig, estado, canvas_config, canvas_fase, animacao)

    # Desenho inicial
    canvas_config.atualizar_estado_inicial(estado)
    canvas_fase.atualizar(estado)
    canvas_config.texto_info.set_text("Pronto para iniciar")

    plt.show()


if __name__ == "__main__":
    main()
