"""
Registro e factory de curvas (fronteiras) do bilhar.
"""

from .circulo import Circulo
from .elipse import Elipse
from .estadio import Estadio
from .poligono import Poligono
from .poligonolivre import PoligonoLivre

CURVAS_DISPONIVEIS: dict[str, type] = {
    "Círculo": Circulo,
    "Elipse": Elipse,
    "Estádio": Estadio,
    "Polígono": Poligono,
    "Polígono Livre": PoligonoLivre,
}

PARAMETROS_CURVA = {
    "Círculo": {"a": "ignorado", "b": "ignorado"},
    "Elipse": {"a": "semi-eixo x", "b": "semi-eixo y"},
    "Estádio": {"a": "semi-comprimento da reta", "b": "raio das tampas"},
    "Polígono": {"a": "número de lados (≥3)", "b": "raio circunscrito"},
    "Polígono Livre": {"a": "ignorado", "b": "ignorado"},
}


def criar_curva(nome: str, **params):
    if nome not in CURVAS_DISPONIVEIS:
        disponiveis = ", ".join(CURVAS_DISPONIVEIS.keys())
        raise ValueError(f"Curva '{nome}' não registrada. Disponíveis: {disponiveis}")
    return CURVAS_DISPONIVEIS[nome](**params)


def listar_curvas() -> list[str]:
    return list(CURVAS_DISPONIVEIS.keys())


__all__ = [
    "Circulo",
    "Elipse",
    "Estadio",
    "Poligono",
    "PoligonoLivre",
    "CURVAS_DISPONIVEIS",
    "PARAMETROS_CURVA",
    "criar_curva",
    "listar_curvas",
]