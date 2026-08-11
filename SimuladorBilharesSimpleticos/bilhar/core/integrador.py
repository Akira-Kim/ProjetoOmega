"""
Integrador event-driven da simulação.
Avança a partícula até a próxima colisão ou pelo dt solicitado.
"""

from __future__ import annotations
import numpy as np
from .estado import EstadoSimulacao
from .fisica import aplicar_colisao, refletir_vetor


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

            # Projeta o ponto exatamente sobre a curva + micro empurrão para dentro
            est.t = t_hit
            est.pos = curva.ponto(est.t) + 1e-9 * est.vel

            # Ângulo com a tangente (para o espaço de fase)
            tg = curva.tangente(est.t)
            est.cos_angulo = float(np.dot(est.vel, tg))

            est.lista_t_colisao.append(est.t / np.pi)
            est.lista_angulo_colisao.append(est.cos_angulo)

            est.traj_x.append(float(est.pos[0]))
            est.traj_y.append(float(est.pos[1]))

            time_left -= lam

        # --- Rede de segurança: se saiu do domínio, corrige ---
        if not self._esta_dentro(est):
            t_corr = curva.t_from_pos(est.pos)
            est.t = t_corr
            est.pos = curva.ponto(t_corr)
            n = curva.normal(est.t)
            est.vel = refletir_vetor(est.vel, n)
            norma = np.linalg.norm(est.vel)
            if norma > 1e-12:
                est.vel /= norma
            est.pos = est.pos + 1e-9 * est.vel

        # Limita o tamanho do histórico de trajetória
        if len(est.traj_x) > 20000:
            est.traj_x = est.traj_x[-10000:]
            est.traj_y = est.traj_y[-10000:]

    def _esta_dentro(self, est) -> bool:
            """Teste simples se a posição está dentro (ou sobre) a curva atual."""
            x, y = float(est.pos[0]), float(est.pos[1])
            nome = est.curva_nome
            a = est.parametro_a
            b = est.parametro_b

            if nome == "Círculo":
                return x * x + y * y <= 1.0 + 1e-4

            if nome == "Elipse":
                return (x / a) ** 2 + (y / b) ** 2 <= 1.0 + 1e-4

            if nome == "Estádio":
                r = b
                if abs(x) <= a:
                    return abs(y) <= r + 1e-4
                cx = a if x > 0 else -a
                return (x - cx) ** 2 + y * y <= r * r + 1e-4

            if nome == "Polígono":
                # Teste de ponto em polígono (ray casting) usando os vértices
                verts = getattr(est.curva, "vertices", None)
                if verts is None:
                    return True
                n = len(verts)
                dentro = False
                j = n - 1
                for i in range(n):
                    xi, yi = verts[i]
                    xj, yj = verts[j]
                    if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-15) + xi):
                        dentro = not dentro
                    j = i
                # margem de tolerância: se estiver muito perto da borda, considera dentro
                if not dentro:
                    # verifica distância mínima aos lados
                    for i in range(n):
                        v0 = verts[i]
                        v1 = verts[(i + 1) % n]
                        d = v1 - v0
                        len2 = np.dot(d, d)
                        if len2 < 1e-14:
                            continue
                        mu = np.clip(np.dot(est.pos - v0, d) / len2, 0.0, 1.0)
                        proj = v0 + mu * d
                        if np.linalg.norm(est.pos - proj) < 1e-3:
                            return True
                return dentro

            return True