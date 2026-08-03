"""
models.py - Funções de acesso ao banco (CRUD)
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
import json

from database import get_connection
from utils.calendar_helpers import (
    parse_dias_semana,
    gerar_datas_aula,
    get_feriados_oficiais_periodo,
    dias_semana_para_texto,
)


# ============================================================
# TURMAS
# ============================================================

def listar_turmas(apenas_ativas: bool = True) -> List[Dict]:
    conn = get_connection()
    if apenas_ativas:
        rows = conn.execute(
            "SELECT * FROM turmas WHERE ativa = 1 ORDER BY nome"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM turmas ORDER BY nome"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obter_turma(turma_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM turmas WHERE id = ?", (turma_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def criar_turma(
    nome: str,
    disciplina: str,
    dias_semana: str,          # "0,2,4" ou "seg,qua,sex"
    data_inicio: str,          # "YYYY-MM-DD"
    data_fim: str,
    cor: str = "#4CAF50",
) -> int:
    """Cria a turma e já gera as aulas. Retorna o id da turma."""
    dias = parse_dias_semana(dias_semana)
    if not dias:
        raise ValueError("Nenhum dia da semana válido informado.")

    dias_str = ",".join(str(d) for d in dias)
    qtd = len(dias)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO turmas (nome, disciplina, dias_semana, qtd_aulas_semana,
                            data_inicio, data_fim, cor)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (nome, disciplina, dias_str, qtd, data_inicio, data_fim, cor),
    )
    turma_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Gera as aulas automaticamente
    gerar_aulas_da_turma(turma_id)
    return turma_id


def atualizar_turma(turma_id: int, **campos) -> None:
    if not campos:
        return
    permitidos = {
        "nome", "disciplina", "dias_semana", "qtd_aulas_semana",
        "data_inicio", "data_fim", "cor", "ativa",
    }
    partes = []
    valores = []
    for k, v in campos.items():
        if k in permitidos:
            partes.append(f"{k} = ?")
            valores.append(v)
    if not partes:
        return
    valores.append(turma_id)
    conn = get_connection()
    conn.execute(
        f"UPDATE turmas SET {', '.join(partes)} WHERE id = ?",
        valores,
    )
    conn.commit()
    conn.close()


def excluir_turma(turma_id: int) -> None:
    """Exclui a turma e todas as aulas ligadas a ela (CASCADE)."""
    conn = get_connection()
    conn.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
    conn.commit()
    conn.close()


# ============================================================
# AULAS
# ============================================================

def _datas_bloqueadas(data_inicio: date, data_fim: date) -> set:
    """Junta feriados oficiais + eventos do tipo feriado/recesso cadastrados."""
    bloqueadas = set()

    # Feriados oficiais BR
    feriados = get_feriados_oficiais_periodo(data_inicio, data_fim, "BR")
    bloqueadas.update(feriados.keys())

    # Eventos manuais de bloqueio
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT data FROM eventos
        WHERE tipo IN ('feriado', 'recesso')
          AND data >= ? AND data <= ?
        """,
        (data_inicio.isoformat(), data_fim.isoformat()),
    ).fetchall()
    conn.close()
    for r in rows:
        bloqueadas.add(date.fromisoformat(r["data"]))

    return bloqueadas


def gerar_aulas_da_turma(turma_id: int, regenerar: bool = True) -> int:
    """
    Gera (ou regenera) as aulas de uma turma.
    Pula feriados oficiais e recessos/feriados manuais.
    Retorna a quantidade de aulas criadas.
    """
    turma = obter_turma(turma_id)
    if not turma:
        raise ValueError(f"Turma {turma_id} não encontrada.")

    inicio = date.fromisoformat(turma["data_inicio"])
    fim = date.fromisoformat(turma["data_fim"])
    dias = parse_dias_semana(turma["dias_semana"])
    bloqueadas = _datas_bloqueadas(inicio, fim)

    datas = gerar_datas_aula(inicio, fim, dias, bloqueadas)

    conn = get_connection()
    cur = conn.cursor()

    if regenerar:
        # Remove aulas antigas que ainda estão só "planejada"
        # (não apaga as que já foram dadas ou têm conteúdo — proteção)
        cur.execute(
            """
            DELETE FROM aulas
            WHERE turma_id = ?
              AND status = 'planejada'
              AND estudada = 0
              AND dada = 0
              AND (conteudo IS NULL OR conteudo = '')
            """,
            (turma_id,),
        )

    criadas = 0
    for d in datas:
        try:
            cur.execute(
                """
                INSERT OR IGNORE INTO aulas (turma_id, data, status)
                VALUES (?, ?, 'planejada')
                """,
                (turma_id, d.isoformat()),
            )
            if cur.rowcount > 0:
                criadas += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    return criadas


def listar_aulas_turma(turma_id: int) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM aulas
        WHERE turma_id = ?
        ORDER BY data
        """,
        (turma_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# EVENTOS
# ============================================================

def listar_eventos(data_inicio: str = None, data_fim: str = None) -> List[Dict]:
    conn = get_connection()
    if data_inicio and data_fim:
        rows = conn.execute(
            """
            SELECT * FROM eventos
            WHERE data >= ? AND data <= ?
            ORDER BY data
            """,
            (data_inicio, data_fim),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM eventos ORDER BY data"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def criar_evento(
    titulo: str,
    data: str,
    tipo: str,
    observacao: str = "",
    cor: str = None,
) -> int:
    cores_padrao = {
        "feriado": "#9C27B0",
        "recesso": "#9C27B0",
        "evento": "#9C27B0",
        "reposicao": "#FF9800",
        "monitoria": "#FF9800",
    }
    if cor is None:
        cor = cores_padrao.get(tipo, "#9C27B0")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO eventos (titulo, data, tipo, observacao, cor)
        VALUES (?, ?, ?, ?, ?)
        """,
        (titulo, data, tipo, observacao, cor),
    )
    evento_id = cur.lastrowid
    conn.commit()
    conn.close()
    return evento_id

def excluir_evento(evento_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
    conn.commit()
    conn.close()


def regenerar_todas_turmas_ativas() -> int:
    """Regenera as aulas de todas as turmas ativas (útil depois de cadastrar recesso)."""
    turmas = listar_turmas(apenas_ativas=True)
    total = 0
    for t in turmas:
        total += gerar_aulas_da_turma(t["id"], regenerar=True)
    return total