"""
Exemplo mínimo de uso da física sem interface gráfica.
Útil para testes e scripts de análise.
"""

import numpy as np
from bilhar.core.estado import EstadoSimulacao
from bilhar.core.integrador import Integrador


def main():
    estado = EstadoSimulacao(
        curva_nome="Elipse",
        a=1.5,
        b=1.0,
        t0=0.0,
        angulo_vel=0.3 * np.pi,
        modo="Simplético",
    )
    estado.pausado = False

    integrador = Integrador(estado)

    print("Rodando 50 passos de simulação (sem gráfico)...")
    for i in range(50):
        integrador.passo(0.05)
        if i % 10 == 0:
            print(
                f"Passo {i:3d} | t={estado.t:.3f} | "
                f"pos=({estado.pos[0]:.3f}, {estado.pos[1]:.3f}) | "
                f"colisões={len(estado.lista_t_colisao)}"
            )

    print(f"\nTotal de colisões registradas: {len(estado.lista_t_colisao)}")


if __name__ == "__main__":
    main()
