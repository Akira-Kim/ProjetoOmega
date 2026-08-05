"""
Curvas paramétricas que definem a fronteira do bilhar.

Fase 1 da reorganização: a classe foi apenas movida para cá, sem
mudança de lógica. Dividir em subclasses por curva (Circulo, Elipse,
Cardioide, ...) é uma melhoria da Fase de extensibilidade, não desta
etapa de organização.
"""
import numpy as np


class CurvaParametrica:
    def __init__(self):
        self.curvas = {
            'Círculo': self.circulo,
            'Elipse': self.elipse
        }
        self.parametro_a = 1.0
        self.parametro_b = 1.0
        self.curva_atual = 'Círculo'

    def __call__(self, t):
        try:
            return self.curvas[self.curva_atual](t)
        except Exception:
            return np.array([0, 0, 0])

    def circulo(self, t):
        return np.array([t, np.cos(t), np.sin(t)])

    def elipse(self, t):
        a, b = self.parametro_a, self.parametro_b
        return np.array([t, a * np.cos(t), b * np.sin(t)])

    def intersect_line(self, point, direction):
        if self.curva_atual == 'Círculo':
            aa = bb = 1.0
        else:
            aa = self.parametro_a
            bb = self.parametro_b

        px, py = point
        dx, dy = direction
        A = (dx / aa) ** 2 + (dy / bb) ** 2
        B = 2 * (px * dx / aa ** 2 + py * dy / bb ** 2)
        C = (px / aa) ** 2 + (py / bb) ** 2 - 1

        disc = B ** 2 - 4 * A * C
        if disc < 0:
            return []
        if A == 0:
            return [0.0]

        sd = np.sqrt(disc)
        l1 = (-B + sd) / (2 * A)
        l2 = (-B - sd) / (2 * A)
        return [l1, l2]

    def get_tangente(self, t):
        if self.curva_atual == 'Círculo':
            return np.array([-np.sin(t), np.cos(t)])
        else:
            a, b = self.parametro_a, self.parametro_b
            d = np.array([-a * np.sin(t), b * np.cos(t)])
            norm = np.linalg.norm(d)
            return d / norm if norm > 1e-12 else np.array([1.0, 0.0])

    def get_normal(self, t):
        tng = self.get_tangente(t)
        return np.array([-tng[1], tng[0]])

    def get_t_from_pos(self, pos_plane):
        x, y = pos_plane
        if self.curva_atual == 'Círculo':
            t = np.arctan2(y, x)
        else:
            a, b = self.parametro_a, self.parametro_b
            t = np.arctan2(y / b, x / a)
        return t if t >= 0 else t + 2 * np.pi
