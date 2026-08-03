"""
utils/calendar_helpers.py
Funções relacionadas a calendário, feriados oficiais e geração de datas de aula.
"""

from datetime import datetime, timedelta, date
from typing import List, Set, Optional
import holidays
import calendar


def get_feriados_oficiais(ano: int, pais: str = "BR") -> dict:
    """
    Retorna um dicionário {date: nome_do_feriado} dos feriados oficiais do país.
    Usa a biblioteca 'holidays'.
    """
    if pais.upper() == "BR":
        feriados = holidays.Brazil(years=ano)
    else:
        # Fallback genérico – pode expandir depois
        feriados = holidays.country_holidays(pais, years=ano)

    return {d: nome for d, nome in feriados.items()}


def get_feriados_oficiais_periodo(data_inicio: date, data_fim: date, pais: str = "BR") -> dict:
    """Retorna feriados oficiais dentro de um período."""
    anos = range(data_inicio.year, data_fim.year + 1)
    todos = {}
    for ano in anos:
        todos.update(get_feriados_oficiais(ano, pais))

    return {
        d: nome for d, nome in todos.items()
        if data_inicio <= d <= data_fim
    }


def gerar_datas_aula(
    data_inicio: date,
    data_fim: date,
    dias_semana: List[int],          # 0=segunda ... 6=domingo
    datas_bloqueadas: Optional[Set[date]] = None
) -> List[date]:
    """
    Gera todas as datas de aula no período, respeitando os dias da semana
    e pulando as datas bloqueadas (feriados + recessos manuais).
    """
    if datas_bloqueadas is None:
        datas_bloqueadas = set()

    datas = []
    atual = data_inicio

    # Ajusta para o primeiro dia válido
    while atual <= data_fim:
        if atual.weekday() in dias_semana and atual not in datas_bloqueadas:
            datas.append(atual)
        atual += timedelta(days=1)

    return datas


def parse_dias_semana(texto: str) -> List[int]:
    """
    Converte string "0,2,4" ou "seg,qua,sex" em lista de inteiros (0-6).
    """
    mapa = {
        "seg": 0, "ter": 1, "qua": 2, "qui": 3, "sex": 4, "sab": 5, "dom": 6,
        "segunda": 0, "terça": 1, "terca": 1, "quarta": 2,
        "quinta": 3, "sexta": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }

    resultado = []
    for parte in texto.lower().replace(" ", "").split(","):
        if parte.isdigit():
            resultado.append(int(parte))
        elif parte in mapa:
            resultado.append(mapa[parte])
    return sorted(set(resultado))


def dias_semana_para_texto(dias: List[int]) -> str:
    """Converte [0,2,4] em 'Seg, Qua, Sex'."""
    nomes = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    return ", ".join(nomes[d] for d in sorted(dias))


def get_semana_atual(referencia: Optional[date] = None) -> List[date]:
    """Retorna lista de 7 datas (segunda a domingo) da semana da data de referência."""
    if referencia is None:
        referencia = date.today()
    inicio = referencia - timedelta(days=referencia.weekday())  # segunda
    return [inicio + timedelta(days=i) for i in range(7)]


def get_mes_calendario(ano: int, mes: int) -> List[List[Optional[date]]]:
    """
    Retorna uma matriz (semanas) do mês para montar o calendário.
    Cada célula é uma date ou None (dias de outros meses).
    """
    cal = calendar.Calendar(firstweekday=0)  # segunda
    semanas = cal.monthdatescalendar(ano, mes)
    # Converte para date e marca None os que não pertencem ao mês
    matriz = []
    for semana in semanas:
        linha = []
        for d in semana:
            if d.month == mes:
                linha.append(d)
            else:
                linha.append(None)
        matriz.append(linha)
    return matriz
