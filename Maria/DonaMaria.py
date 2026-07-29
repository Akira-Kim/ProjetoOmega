#!/usr/bin/env python3
# ============================================================
#  Dona Maria — versão CONSOLE (terminal)
#  A lógica fica em chat.py
# ============================================================

import chat as pc

nome_maquina = "Maria"

pc.saudacoes(nome_maquina)

while True:
    texto = pc.recebeTexto()

    if texto is None:
        continue

    resposta = pc.buscaResposta(texto)

    if pc.exibeResposta(resposta, nome_maquina) == "fim":
        break
