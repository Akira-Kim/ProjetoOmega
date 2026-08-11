"""
Núcleo físico do simulador de bilhares.
Não deve depender de bibliotecas gráficas.
"""

from .curva import CurvaBase
from .estado import EstadoSimulacao
from .fisica import refletir_vetor, aplicar_colisao
from .integrador import Integrador

__all__ = [
    "CurvaBase",
    "EstadoSimulacao",
    "refletir_vetor",
    "aplicar_colisao",
    "Integrador",
]
