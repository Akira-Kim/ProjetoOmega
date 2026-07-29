import chat as pc
from tkinter import *
import re

# ============================
# CONFIGURAÇÃO DA JANELA
# ============================

nome_maquina = "Maria"

main_window = Tk()
main_window.title("Chatbot Dona Maria")
main_window.geometry("700x600")

# ============================
# VARIÁVEIS
# ============================

historico = ""
entrada_sugestao = False
ultima_pergunta = ""

# ============================
# HISTÓRICO
# ============================

texto_conversa = Text(
    main_window,
    width=80,
    height=25,
    state=DISABLED,
    wrap=WORD
)

texto_conversa.pack(pady=10)

# ============================
# ENTRADA
# ============================

frame = Frame(main_window)
frame.pack()

entrada = Entry(frame, width=60)
entrada.grid(row=0, column=0, padx=5)

# ============================
# FUNÇÕES
# ============================

def escrever(mensagem):

    texto_conversa.config(state=NORMAL)

    texto_conversa.insert(END, mensagem + "\n")

    texto_conversa.config(state=DISABLED)

    texto_conversa.see(END)


def contem_palavra_proibida(texto):
    texto_normalizado = pc.normalizar(texto)
    for palavra in pc.PALAVRAS_PROIBIDAS:
        if re.search(rf"\b{re.escape(pc.remover_acentos(palavra.lower()))}\b",
                     texto_normalizado):
            return True
    return False


def enviar(event=None):

    global entrada_sugestao
    global ultima_pergunta

    texto = entrada.get().strip()

    if texto == "":
        return

    entrada.delete(0, END)

    escrever("Você: " + texto)

    # Filtro de palavras proibidas (exceto quando está sugerindo resposta)
    if not entrada_sugestao and contem_palavra_proibida(texto):
        escrever(nome_maquina + ": Desculpe, não posso responder esse tipo de mensagem.")
        return

    if entrada_sugestao:

        pc.salva_sugestao(ultima_pergunta, texto)

        escrever(nome_maquina + ": Obrigado! Aprendi uma nova resposta.")

        entrada_sugestao = False

        return

    # Verificar despedida
    pergunta = pc.normalizar(texto)
    if pergunta in ["tchau", "adeus", "até logo", "ate logo"]:
        escrever(nome_maquina + ": Volte sempre!")
        return

    resposta = pc.buscaResposta_GUI(texto)

    if resposta is None:

        escrever(nome_maquina + ": Não sei responder isso.")

        escrever(nome_maquina + ": Qual deveria ser a resposta?")

        ultima_pergunta = texto

        entrada_sugestao = True

    else:

        escrever(nome_maquina + ": " + resposta)

# ============================
# BOTÃO
# ============================

Button(
    frame,
    text="Enviar",
    command=enviar
).grid(row=0, column=1)

entrada.bind("<Return>", enviar)

# ============================
# MENSAGEM INICIAL
# ============================

escrever(pc.saudacoes_GUI(nome_maquina))

entrada.focus()

main_window.mainloop()