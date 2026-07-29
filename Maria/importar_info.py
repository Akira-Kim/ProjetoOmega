import sqlite3
import os
import unicodedata
import re

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DB = os.path.join(PASTA, "conhecimento.db")
ARQUIVO_TXT = os.path.join(PASTA, "info.txt")


def remover_acentos(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def normalizar(texto):
    texto = texto.lower().strip()
    texto = remover_acentos(texto)
    texto = re.sub(r"[^\w\s]", "", texto)
    return texto


if not os.path.exists(ARQUIVO_TXT):
    print("ERRO: info.txt não encontrado em:")
    print(" ", PASTA)
    raise SystemExit(1)

conexao = sqlite3.connect(ARQUIVO_DB)
cursor = conexao.cursor()

inseridos = 0
ignorados = 0

with open(ARQUIVO_TXT, "r", encoding="utf-8") as arquivo:
    for linha in arquivo:
        linha = linha.strip()
        if ";" not in linha:
            continue

        pergunta_bruta, resposta = linha.split(";", 1)
        pergunta = normalizar(pergunta_bruta)
        resposta = resposta.strip()

        if not pergunta or not resposta:
            ignorados += 1
            continue

        # Evita duplicar a mesma pergunta+resposta
        cursor.execute(
            """
            SELECT id FROM conhecimento
            WHERE pergunta = ? AND resposta = ?
            """,
            (pergunta, resposta),
        )
        if cursor.fetchone():
            ignorados += 1
            continue

        cursor.execute(
            """
            INSERT INTO conhecimento (pergunta, resposta)
            VALUES (?, ?)
            """,
            (pergunta, resposta),
        )
        inseridos += 1

conexao.commit()

# Conta quantas linhas ficaram no banco
cursor.execute("SELECT COUNT(*) FROM conhecimento")
total = cursor.fetchone()[0]

conexao.close()

print("Importação concluída.")
print(f"  Inseridos : {inseridos}")
print(f"  Ignorados : {ignorados}")
print(f"  Total no banco: {total}")