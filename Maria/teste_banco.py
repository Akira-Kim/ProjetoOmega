import sqlite3
import os

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DB = os.path.join(PASTA, "conhecimento.db")

conexao = sqlite3.connect(ARQUIVO_DB)
cursor = conexao.cursor()

cursor.execute("SELECT COUNT(*) FROM conhecimento")
print("Total de registros:", cursor.fetchone()[0])

print("\nExemplos com 'python':")
cursor.execute(
    """
    SELECT pergunta, resposta
    FROM conhecimento
    WHERE pergunta LIKE '%python%'
    LIMIT 5
    """
)
for pergunta, resposta in cursor.fetchall():
    print("-", pergunta, "->", resposta[:60])

print("\nExemplos com ' o que e c':")
cursor.execute(
    """
    SELECT pergunta, resposta
    FROM conhecimento
    WHERE pergunta = 'o que e c'
    """
)
for pergunta, resposta in cursor.fetchall():
    print("-", pergunta, "->", resposta)

conexao.close()
print("\nOK — banco legível.")