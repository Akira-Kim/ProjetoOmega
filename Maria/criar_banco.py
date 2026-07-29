import sqlite3
import os

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DB = os.path.join(PASTA, "conhecimento.db")

conexao = sqlite3.connect(ARQUIVO_DB)
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS conhecimento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    vezes_usada INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# Índice para busca mais rápida pela pergunta
cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_pergunta
ON conhecimento (pergunta)
""")

conexao.commit()
conexao.close()

print("Banco criado com sucesso:")
print(" ", ARQUIVO_DB)
print("Tabela: conhecimento")