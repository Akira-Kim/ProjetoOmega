"""
database.py - Conexão e criação das tabelas do GerenciadorDeTurmas
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# Caminho do banco (fica dentro da pasta data/)
# Em alguns ambientes (sandbox) o FS especial pode não suportar SQLite bem.
# Tentamos a pasta data/ do projeto; se falhar, usamos /tmp.
_PROJECT_DB = Path(__file__).parent / "data" / "planner.db"
_FALLBACK_DB = Path("/tmp/GerenciadorDeTurmas/planner.db")


def _escolher_db_path() -> Path:
    """Escolhe um caminho de banco que funcione no ambiente atual."""
    try:
        _PROJECT_DB.parent.mkdir(parents=True, exist_ok=True)
        test_conn = sqlite3.connect(str(_PROJECT_DB))
        test_conn.execute("CREATE TABLE IF NOT EXISTS _teste_io (x INTEGER)")
        test_conn.execute("DROP TABLE IF EXISTS _teste_io")
        test_conn.close()
        return _PROJECT_DB
    except Exception:
        _FALLBACK_DB.parent.mkdir(parents=True, exist_ok=True)
        print(f"⚠️  Usando banco em fallback: {_FALLBACK_DB}")
        return _FALLBACK_DB


DB_PATH = _escolher_db_path()


def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # permite acessar colunas por nome
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_tabelas():
    """Cria todas as tabelas se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    # ---------------------------
    # TURMAS
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            disciplina TEXT,
            dias_semana TEXT NOT NULL,          -- ex: "0,2,4" (seg=0 ... dom=6)
            qtd_aulas_semana INTEGER DEFAULT 1,
            data_inicio TEXT NOT NULL,          -- YYYY-MM-DD
            data_fim TEXT NOT NULL,             -- YYYY-MM-DD
            cor TEXT DEFAULT "#4CAF50",
            ativa INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------------------
    # AULAS (geradas a partir das turmas)
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aulas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turma_id INTEGER NOT NULL,
            data TEXT NOT NULL,                 -- YYYY-MM-DD
            status TEXT DEFAULT 'planejada',    -- planejada | estudada | dada | cancelada | adiada
            estudada INTEGER DEFAULT 0,
            dada INTEGER DEFAULT 0,
            conteudo TEXT,
            links TEXT,                         -- JSON ou texto separado por ;
            imagem BLOB,                        -- imagem principal (opcional)
            observacao TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
            UNIQUE(turma_id, data)
        )
    """)

    # ---------------------------
    # EVENTOS (feriados, recessos, reposições, monitorias, eventos únicos)
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data TEXT NOT NULL,                 -- YYYY-MM-DD
            tipo TEXT NOT NULL,                 -- feriado | recesso | evento | reposicao | monitoria
            observacao TEXT,
            cor TEXT,                           -- se NULL usa a cor padrão do tipo
            dia_todo INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------------------------
    # ALUNOS
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turma_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            observacao TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE
        )
    """)

    # ---------------------------
    # REGISTROS POR AULA + ALUNO (nota, coins, análise)
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros_aula (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aula_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            nota_dia REAL,
            coins INTEGER DEFAULT 0,
            analise TEXT,
            data_registro TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (aula_id) REFERENCES aulas(id) ON DELETE CASCADE,
            FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
            UNIQUE(aula_id, aluno_id)
        )
    """)

    # ---------------------------
    # RELATÓRIOS (de aula ou de aluno gerados por IA)
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,                 -- aula | aluno
            aula_id INTEGER,                    -- se for relatório de aula
            aluno_id INTEGER,                   -- se for relatório de aluno
            turma_id INTEGER,
            titulo TEXT,
            conteudo TEXT NOT NULL,
            modelo_usado TEXT,                  -- nome do arquivo de modelo (quando IA)
            data_geracao TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (aula_id) REFERENCES aulas(id) ON DELETE SET NULL,
            FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE SET NULL,
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE SET NULL
        )
    """)

    # ---------------------------
    # CONFIGURAÇÕES
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)

    # Valores padrão de configuração
    cursor.execute("""
        INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES
        ('ano_letivo', ?),
        ('pais_feriados', 'BR'),
        ('ia_provider', 'groq'),
        ('ia_api_key', ''),
        ('tema', 'system')
    """, (str(datetime.now().year),))

    conn.commit()
    conn.close()
    print(f"✅ Banco de dados criado/verificado em: {DB_PATH}")


def inicializar_banco():
    """Garante que a pasta data existe e cria as tabelas."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    criar_tabelas()


if __name__ == "__main__":
    inicializar_banco()
