"""
Integrador event-driven da simulação.
Avança a partícula até a próxima colisão ou pelo dt solicitado.
"""

from __future__ import annotations
import numpy as np
from .estado import EstadoSimulacao
from .fisica import aplicar_colisao


class Integrador:
    def __init__(self, estado: EstadoSimulacao):
        self.estado = estado

    def passo(self, dt: float) -> None:
        """
        Avança a simulação por no máximo `dt` unidades de tempo.
        Pode ocorrer zero ou mais colisões dentro desse intervalo.
        """
        if self.estado.pausado:
            return

        time_left = dt
        est = self.estado
        curva = est.curva

        while time_left > 1e-8:
            lambdas = curva.intersect_line(est.pos, est.vel)
            positive_lams = [lam for lam in lambdas if lam > 1e-8]

            if not positive_lams:
                # Sem interseção futura (não deveria acontecer em curvas fechadas)
                est.pos = est.pos + est.vel * time_left
                est.traj_x.append(float(est.pos[0]))
                est.traj_y.append(float(est.pos[1]))
                break

            lam = min(positive_lams)

            if lam >= time_left:
                est.pos = est.pos + est.vel * time_left
                est.traj_x.append(float(est.pos[0]))
                est.traj_y.append(float(est.pos[1]))
                break

            # Colisão
            hit_pos = est.pos + lam * est.vel
            est.traj_x.append(float(hit_pos[0]))
            est.traj_y.append(float(hit_pos[1]))

            t_hit = curva.t_from_pos(hit_pos)

            nova_vel, aux_x, aux_y = aplicar_colisao(
                modo=est.modo_bilhar,
                curva=curva,
                t_hit=t_hit,
                hit_pos=hit_pos,
                vel=est.vel,
                t_anterior=est.t,
            )

            est.vel = nova_vel
            est.trajetoria_aux_x = aux_x
            est.trajetoria_aux_y = aux_y

            # Pequeno empurrão para fora da superfície
            est.pos = hit_pos + 1e-8 * est.vel
            est.t = t_hit

            # Ângulo com a tangente (para o espaço de fase)
            tg = curva.tangente(est.t)
            est.cos_angulo = float(np.dot(est.vel, tg))

            est.lista_t_colisao.append(est.t / np.pi)
            est.lista_angulo_colisao.append(est.cos_angulo)

            est.traj_x.append(float(est.pos[0]))
            est.traj_y.append(float(est.pos[1]))

            time_left -= lam

        # Limita o tamanho do histórico de trajetória
        if len(est.traj_x) > 20000:
            est.traj_x = est.traj_x[-10000:]
            est.traj_y = est.traj_y[-10000:]
