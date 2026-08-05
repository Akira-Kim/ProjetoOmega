"""
Avanço da simulação no tempo.

step(estado, dt) é a fronteira entre física e visualização: recebe o
estado atual, avança dt segundos (com sub-passos até a próxima colisão
dentro de dt) e devolve a lista de colisões ocorridas nesse intervalo.
Não desenha nada — quem decide o que fazer com os eventos é a camada
de visualização (Fase 2).
"""
import numpy as np

from .fisica import refletir_vetor


def step(estado, dt):
    eventos_colisao = []
    time_left = dt
    curva = estado.curva_parametrica

    while time_left > 1e-8:
        lambdas = curva.intersect_line(estado.pos, estado.vel)
        positive_lams = [lam for lam in lambdas if lam > 1e-8]

        if not positive_lams:
            estado.pos = estado.pos + estado.vel * time_left
            estado.traj_x.append(estado.pos[0])
            estado.traj_y.append(estado.pos[1])
            break

        lam = min(positive_lams)

        if lam >= time_left:
            estado.pos = estado.pos + estado.vel * time_left
            estado.traj_x.append(estado.pos[0])
            estado.traj_y.append(estado.pos[1])
            break

        hit_pos = estado.pos + lam * estado.vel
        estado.traj_x.append(hit_pos[0])
        estado.traj_y.append(hit_pos[1])

        t_hit = curva.get_t_from_pos(hit_pos)
        trajetoria_aux = None  # pontos da corda auxiliar, só no modo simplético

        if estado.modo_bilhar == 'Elástico':
            n = curva.get_normal(t_hit)
            estado.vel = refletir_vetor(estado.vel, n)
            estado.trajetoria_aux_x = []
            estado.trajetoria_aux_y = []

        else:  # Simplético
            x_pos = np.array([curva(estado.t)[1], curva(estado.t)[2]])
            T = curva.get_tangente(t_hit)
            lambdas_sym = curva.intersect_line(x_pos, T)
            other_lambda = 0.0
            for l in lambdas_sym:
                if abs(l) > 1e-6:
                    other_lambda = l
                    break
            z_pos = x_pos + other_lambda * T

            if np.linalg.norm(z_pos - hit_pos) < 1e-8:
                n = curva.get_normal(t_hit)
                estado.vel = refletir_vetor(estado.vel, n)
            else:
                estado.vel = (z_pos - hit_pos)
                estado.vel = estado.vel / np.linalg.norm(estado.vel)

            estado.trajetoria_aux_x = [x_pos[0], z_pos[0]]
            estado.trajetoria_aux_y = [x_pos[1], z_pos[1]]
            trajetoria_aux = (list(estado.trajetoria_aux_x), list(estado.trajetoria_aux_y))

        estado.pos = hit_pos.copy() + 1e-8 * estado.vel
        estado.t = t_hit

        tg = curva.get_tangente(estado.t)
        estado.cos_angulo = float(np.dot(estado.vel, tg))

        estado.lista_t_colisao.append(estado.t / np.pi)
        estado.lista_angulo_colisao.append(estado.cos_angulo)

        eventos_colisao.append({
            "t_normalizado": estado.t / np.pi,
            "cos_angulo": estado.cos_angulo,
            "trajetoria_aux": trajetoria_aux,
        })

        estado.traj_x.append(estado.pos[0])
        estado.traj_y.append(estado.pos[1])

        time_left -= lam

    if len(estado.traj_x) > 20000:
        estado.traj_x = estado.traj_x[-10000:]
        estado.traj_y = estado.traj_y[-10000:]

    return eventos_colisao
