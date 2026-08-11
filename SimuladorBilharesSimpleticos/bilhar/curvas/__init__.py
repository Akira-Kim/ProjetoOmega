"""
Registro e factory de curvas (fronteiras) do bilhar.

Para adicionar uma nova curva:
1. Crie o arquivo em bilhar/curvas/minha_curva.py herdando de CurvaBase
2. Importe e registre abaixo em CURVAS_DISPONIVEIS
3. (Opcional) Atualize a lista do RadioButtons em ui/controles.py
"""

from .circulo import Circulo
from .elipse import Elipse
from .estadio import Estadio
from .poligono import Poligono

# Registro central – única fonte de verdade
CURVAS_DISPONIVEIS: dict[str, type] = {
    "Círculo": Circulo,
    "Elipse": Elipse,
    "Estádio": Estadio,
    "Polígono": Poligono,
}

# Descrição curta dos parâmetros
PARAMETROS_CURVA = {
    "Círculo":  {"a": "ignorado", "b": "ignorado"},
    "Elipse":   {"a": "semi-eixo x", "b": "semi-eixo y"},
    "Estádio":  {"a": "semi-comprimento da reta", "b": "raio das tampas"},
    "Polígono": {"a": "número de lados (≥3)", "b": "raio circunscrito"},
}


def criar_curva(nome: str, **params):
    """Factory: cria uma instância da curva pelo nome."""
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
    "CURVAS_DISPONIVEIS",
    "PARAMETROS_CURVA",
    "criar_curva",
    "listar_curvas",
]