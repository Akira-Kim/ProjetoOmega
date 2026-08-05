"""
models.py - Funções de acesso ao banco (CRUD)
"""
from datetime import datetime, date, timedelta
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

def obter_aula(aula_id: int):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT a.*, t.nome AS turma_nome, t.disciplina, t.cor AS turma_cor
        FROM aulas a
        JOIN turmas t ON t.id = a.turma_id
        WHERE a.id = ?
        """,
        (aula_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def atualizar_aula(aula_id: int, **campos) -> None:
    permitidos = {
        "status", "estudada", "dada", "conteudo", "links",
        "observacao", "data",
    }
    partes, valores = [], []
    for k, v in campos.items():
        if k in permitidos:
            partes.append(f"{k} = ?")
            valores.append(v)
    if not partes:
        return
    valores.append(aula_id)
    conn = get_connection()
    conn.execute(
        f"UPDATE aulas SET {', '.join(partes)} WHERE id = ?",
        valores,
    )
    conn.commit()
    conn.close()


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

def _proxima_data_valida(depois_de: date, dias_semana: list, bloqueadas: set, data_fim: date) -> date | None:
    """Próxima data > depois_de que cai num dia da semana da turma e não está bloqueada."""
    atual = depois_de + timedelta(days=1)
    while atual <= data_fim:
        if atual.weekday() in dias_semana and atual not in bloqueadas:
            return atual
        atual += timedelta(days=1)
    return None


def remarcar_aula(aula_id: int, nova_data_str: str) -> str:
    """
    Remarca uma aula.
    Se a nova data já tiver aula da mesma turma, empurra essa e todas as
    seguintes uma ocorrência para frente.
    Retorna mensagem descritiva.
    """
    from datetime import timedelta  # se ainda não importou no topo

    conn = get_connection()
    aula = conn.execute("SELECT * FROM aulas WHERE id = ?", (aula_id,)).fetchone()
    if not aula:
        conn.close()
        raise ValueError("Aula não encontrada.")

    turma = conn.execute("SELECT * FROM turmas WHERE id = ?", (aula["turma_id"],)).fetchone()
    if not turma:
        conn.close()
        raise ValueError("Turma não encontrada.")

    nova_data = date.fromisoformat(nova_data_str)
    turma_id = aula["turma_id"]
    dias = parse_dias_semana(turma["dias_semana"])
    inicio = date.fromisoformat(turma["data_inicio"])
    fim = date.fromisoformat(turma["data_fim"])
    bloqueadas = _datas_bloqueadas(inicio, fim)

    # Já está nessa data?
    if aula["data"] == nova_data_str:
        conn.close()
        return "Aula já está nessa data."

    # Existe outra aula da mesma turma nessa data?
    conflito = conn.execute(
        """
        SELECT * FROM aulas
        WHERE turma_id = ? AND data = ? AND id != ?
        """,
        (turma_id, nova_data_str, aula_id),
    ).fetchone()

    if not conflito:
        # Sem conflito: só atualiza
        conn.execute("UPDATE aulas SET data = ? WHERE id = ?", (nova_data_str, aula_id))
        conn.commit()
        conn.close()
        return f"Aula remarcada para {nova_data_str}."

    # ----- Há conflito: empurrar para frente -----
    # Todas as aulas desta turma com data >= nova_data, exceto a que estamos movendo
    para_empurrar = conn.execute(
        """
        SELECT id, data FROM aulas
        WHERE turma_id = ? AND data >= ? AND id != ?
        ORDER BY data ASC
        """,
        (turma_id, nova_data_str, aula_id),
    ).fetchall()

    # Calcula as novas datas (da última para a primeira, para não violar UNIQUE)
    # Sequência desejada:
    #   aula movida → nova_data
    #   1ª empurrada → próxima válida depois de nova_data
    #   2ª empurrada → próxima válida depois da anterior
    #   ...
    novas_datas = []  # lista de (id, nova_data_str)
    cursor_data = nova_data

    for row in para_empurrar:
        prox = _proxima_data_valida(cursor_data, dias, bloqueadas, fim)
        if prox is None:
            conn.close()
            raise ValueError(
                "Não há datas suficientes no período da turma para empurrar as aulas. "
                "Aumente a data fim da turma ou remarque para outra data."
            )
        novas_datas.append((row["id"], prox.isoformat()))
        cursor_data = prox

    # Atualiza de trás para frente (evita conflito de UNIQUE)
    for aid, d in reversed(novas_datas):
        conn.execute("UPDATE aulas SET data = ? WHERE id = ?", (d, aid))

    # Por fim, coloca a aula movida na data escolhida
    conn.execute("UPDATE aulas SET data = ? WHERE id = ?", (nova_data_str, aula_id))
    conn.commit()
    conn.close()

    n = len(novas_datas)
    return (
        f"Aula movida para {nova_data_str}. "
        f"{n} aula(s) seguinte(s) foram empurradas para frente."
    )

def listar_aulas_periodo(data_inicio: str, data_fim: str) -> list:
    """Aulas no periodo, com dados da turma."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT a.*, t.nome AS turma_nome, t.disciplina, t.cor AS turma_cor
        FROM aulas a
        JOIN turmas t ON t.id = a.turma_id
        WHERE a.data >= ? AND a.data <= ?
          AND t.ativa = 1
        ORDER BY a.data, t.nome
        """,
        (data_inicio, data_fim),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obter_aula(aula_id: int):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT a.*, t.nome AS turma_nome, t.disciplina, t.cor AS turma_cor
        FROM aulas a
        JOIN turmas t ON t.id = a.turma_id
        WHERE a.id = ?
        """,
        (aula_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def atualizar_aula(aula_id: int, **campos) -> None:
    permitidos = {
        "status", "estudada", "dada", "conteudo", "links",
        "observacao", "data",
    }
    partes, valores = [], []
    for k, v in campos.items():
        if k in permitidos:
            partes.append(f"{k} = ?")
            valores.append(v)
    if not partes:
        return
    valores.append(aula_id)
    conn = get_connection()
    conn.execute(
        f"UPDATE aulas SET {', '.join(partes)} WHERE id = ?",
        valores,
    )
    conn.commit()
    conn.close()

# ============================================================
# ALUNOS
# ============================================================

def listar_alunos(turma_id: int, apenas_ativos: bool = True) -> list:
    conn = get_connection()
    if apenas_ativos:
        rows = conn.execute(
            """
            SELECT * FROM alunos
            WHERE turma_id = ? AND ativo = 1
            ORDER BY nome
            """,
            (turma_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT * FROM alunos
            WHERE turma_id = ?
            ORDER BY nome
            """,
            (turma_id,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def contar_alunos(turma_id: int) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM alunos WHERE turma_id = ? AND ativo = 1",
        (turma_id,),
    ).fetchone()
    conn.close()
    return row["n"] if row else 0


def criar_aluno(turma_id: int, nome: str, observacao: str = "") -> int:
    nome = (nome or "").strip()
    if not nome:
        raise ValueError("Nome do aluno e obrigatorio.")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO alunos (turma_id, nome, observacao, ativo)
        VALUES (?, ?, ?, 1)
        """,
        (turma_id, nome, observacao or ""),
    )
    aluno_id = cur.lastrowid
    conn.commit()
    conn.close()
    return aluno_id


def atualizar_aluno(aluno_id: int, **campos) -> None:
    permitidos = {"nome", "observacao", "ativo", "turma_id"}
    partes, valores = [], []
    for k, v in campos.items():
        if k in permitidos:
            partes.append(f"{k} = ?")
            valores.append(v)
    if not partes:
        return
    valores.append(aluno_id)
    conn = get_connection()
    conn.execute(
        f"UPDATE alunos SET {', '.join(partes)} WHERE id = ?",
        valores,
    )
    conn.commit()
    conn.close()


def desativar_aluno(aluno_id: int) -> None:
    atualizar_aluno(aluno_id, ativo=0)


def obter_resumo_aluno(aluno_id: int) -> dict:
    """Media de notas, total de coins e qtd de registros."""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS qtd_registros,
            AVG(nota_dia) AS media_notas,
            SUM(coins) AS total_coins
        FROM registros_aula
        WHERE aluno_id = ?
        """,
        (aluno_id,),
    ).fetchone()
    conn.close()
    return {
        "qtd_registros": row["qtd_registros"] or 0,
        "media_notas": round(row["media_notas"], 2) if row["media_notas"] is not None else None,
        "total_coins": row["total_coins"] or 0,
    }

# ============================================================
# REGISTROS POR AULA + ALUNO
# ============================================================

def listar_registros_aula(aula_id: int) -> list:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT r.*, al.nome AS aluno_nome
        FROM registros_aula r
        JOIN alunos al ON al.id = r.aluno_id
        WHERE r.aula_id = ?
        ORDER BY al.nome
        """,
        (aula_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def salvar_registro_aula(
    aula_id: int,
    aluno_id: int,
    nota_dia=None,
    coins: int = 0,
    analise: str = "",
) -> None:
    """Insere ou atualiza o registro do aluno naquela aula."""
    conn = get_connection()
    existente = conn.execute(
        """
        SELECT id FROM registros_aula
        WHERE aula_id = ? AND aluno_id = ?
        """,
        (aula_id, aluno_id),
    ).fetchone()

    if existente:
        conn.execute(
            """
            UPDATE registros_aula
            SET nota_dia = ?, coins = ?, analise = ?, data_registro = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (nota_dia, coins or 0, analise or "", existente["id"]),
        )
    else:
        conn.execute(
            """
            INSERT INTO registros_aula (aula_id, aluno_id, nota_dia, coins, analise)
            VALUES (?, ?, ?, ?, ?)
            """,
            (aula_id, aluno_id, nota_dia, coins or 0, analise or ""),
        )
    conn.commit()
    conn.close()


def listar_alunos_com_registro(aula_id: int, turma_id: int) -> list:
    alunos = listar_alunos(turma_id, apenas_ativos=True)
    registros = {r["aluno_id"]: r for r in listar_registros_aula(aula_id)}
    resultado = []
    for al in alunos:
        reg = registros.get(al["id"], {})
        resultado.append({
            "aluno_id": al["id"],
            "nome": al["nome"],
            "nota_dia": reg.get("nota_dia"),
            "coins": reg.get("coins") if reg.get("coins") is not None else 0,
            "analise": reg.get("analise") or "",
        })
    return resultado

# ============================================================
# RELATORIOS
# ============================================================

def criar_relatorio_aula(
    aula_id: int,
    conteudo: str,
    titulo: str = "",
    turma_id: int = None,
) -> int:
    conteudo = (conteudo or "").strip()
    if not conteudo:
        raise ValueError("Relatorio vazio.")

    aula = obter_aula(aula_id)
    if turma_id is None and aula:
        turma_id = aula["turma_id"]
    if not titulo:
        titulo = f"Relatorio aula {aula['data']}" if aula else "Relatorio de aula"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO relatorios (tipo, aula_id, turma_id, titulo, conteudo)
        VALUES ('aula', ?, ?, ?, ?)
        """,
        (aula_id, turma_id, titulo, conteudo),
    )
    rid = cur.lastrowid
    conn.commit()
    conn.close()
    return rid

def listar_relatorios(
    tipo: str = None,
    turma_id: int = None,
    aula_id: int = None,
) -> list:
    conn = get_connection()
    sql = "SELECT * FROM relatorios WHERE 1=1"
    params = []
    if tipo:
        sql += " AND tipo = ?"
        params.append(tipo)
    if turma_id:
        sql += " AND turma_id = ?"
        params.append(turma_id)
    if aula_id:
        sql += " AND aula_id = ?"
        params.append(aula_id)
    sql += " ORDER BY data_geracao DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obter_relatorio(relatorio_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM relatorios WHERE id = ?", (relatorio_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def atualizar_relatorio(relatorio_id: int, titulo: str = None, conteudo: str = None) -> None:
    partes, valores = [], []
    if titulo is not None:
        partes.append("titulo = ?")
        valores.append(titulo)
    if conteudo is not None:
        partes.append("conteudo = ?")
        valores.append(conteudo)
    if not partes:
        return
    valores.append(relatorio_id)
    conn = get_connection()
    conn.execute(
        f"UPDATE relatorios SET {', '.join(partes)} WHERE id = ?",
        valores,
    )
    conn.commit()
    conn.close()


def excluir_relatorio(relatorio_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM relatorios WHERE id = ?", (relatorio_id,))
    conn.commit()
    conn.close()

def listar_historico_aluno(aluno_id: int) -> list:
    """Registros do aluno com data e turma da aula."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            r.id AS registro_id,
            r.nota_dia,
            r.coins,
            r.analise,
            r.data_registro,
            a.id AS aula_id,
            a.data AS data_aula,
            a.status AS status_aula,
            t.nome AS turma_nome
        FROM registros_aula r
        JOIN aulas a ON a.id = r.aula_id
        JOIN turmas t ON t.id = a.turma_id
        WHERE r.aluno_id = ?
        ORDER BY a.data DESC
        """,
        (aluno_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def obter_aluno(aluno_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM alunos WHERE id = ?", (aluno_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def montar_contexto_aluno(aluno_id: int) -> str:
    """Texto com dados do aluno para colar no prompt da IA."""
    aluno = obter_aluno(aluno_id)
    if not aluno:
        raise ValueError("Aluno nao encontrado.")

    resumo = obter_resumo_aluno(aluno_id)
    historico = listar_historico_aluno(aluno_id)
    turma = obter_turma(aluno["turma_id"]) if aluno.get("turma_id") else None

    media = resumo["media_notas"]
    media_txt = f"{media:.2f}" if media is not None else "sem notas"
    linhas = [
        f"Nome: {aluno.get('nome')}",
        f"Turma: {turma.get('nome') if turma else '—'}",
        f"Disciplina: {turma.get('disciplina') if turma else '—'}",
        f"Observacao geral do aluno: {aluno.get('observacao') or '—'}",
        f"Media de notas: {media_txt}",
        f"Total de coins: {resumo['total_coins']}",
        f"Quantidade de registros (aulas com lancamento): {resumo['qtd_registros']}",
        "",
        "Historico aula a aula (mais recente primeiro):",
    ]
    if not historico:
        linhas.append("  (nenhum registro)")
    else:
        for h in historico:
            nota = h["nota_dia"] if h["nota_dia"] is not None else "—"
            coins = h.get("coins") if h.get("coins") is not None else 0
            analise = (h.get("analise") or "").strip() or "—"
            linhas.append(
                f"  - Data {h['data_aula']} | nota={nota} | coins={coins} | "
                f"status={h.get('status_aula') or '—'} | analise: {analise}"
            )
    return "\n".join(linhas)


def montar_prompt_relatorio(modelo: str, contexto_aluno: str) -> str:
    """
    Se o modelo tiver {{dados}}, substitui.
    Senao, anexa os dados no final.
    """
    modelo = (modelo or "").strip()
    if "{{dados}}" in modelo:
        return modelo.replace("{{dados}}", contexto_aluno)
    return (
        f"{modelo}\n\n"
        f"--- DADOS DO ALUNO ---\n"
        f"{contexto_aluno}\n"
        f"--- FIM DOS DADOS ---\n"
    )


def criar_relatorio_aluno(
    aluno_id: int,
    conteudo: str,
    titulo: str = "",
    modelo_usado: str = "",
    turma_id: int = None,
) -> int:
    conteudo = (conteudo or "").strip()
    if not conteudo:
        raise ValueError("Relatorio vazio.")
    aluno = obter_aluno(aluno_id)
    if turma_id is None and aluno:
        turma_id = aluno.get("turma_id")
    if not titulo:
        nome = aluno.get("nome") if aluno else "aluno"
        titulo = f"Relatorio do aluno — {nome}"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO relatorios (tipo, aluno_id, turma_id, titulo, conteudo, modelo_usado)
        VALUES ('aluno', ?, ?, ?, ?, ?)
        """,
        (aluno_id, turma_id, titulo, conteudo, modelo_usado or ""),
    )
    rid = cur.lastrowid
    conn.commit()
    conn.close()
    return rid