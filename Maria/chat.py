import random
import re
import unicodedata
import difflib
import os
import sqlite3

_PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DB = os.path.join(_PASTA, "conhecimento.db")

# Limiar do Jaccard (palavras em comum)
LIMIAR_JACCARD = 0.40

# Limiar do difflib (parecido letra a letra) — 0.0 a 1.0
LIMIAR_DIGITACAO = 0.72

# ==============================
# PALAVRAS PROIBIDAS
# ==============================

PALAVRAS_PROIBIDAS = [
    "idiota", "burro", "otario", "otário", "babaca",
    "imbecil", "otaria", "otária", "palhaço", "palhaco",
    "trouxa", "retardado", "animal", "tapado",

    "merda", "bosta", "porra", "caralho",
    "cacete", "puta", "puta que pariu", "fdp",
    "filho da puta", "desgraçado", "desgracado",
    "arrombado", "arrombada", "cu", "cú",

    "vagabundo", "vagabunda", "lixo",
    "escroto", "escrota", "nojento", "nojenta",

    "gostosa", "gostoso", "delicia", "delícia",
    "manda nude", "nudes", "pelada", "pelado",

    "http://", "https://", "www.",
    ".com", ".net", ".xyz",

    "pix urgente", "ganhe dinheiro",
    "aposta", "cassino", "jogo do tigrinho",

    "cocaina", "cocaína", "maconha",
    "crack", "heroina", "heroína",

    "sexo", "porno", "pornografia",
    "hentai", "onlyfans"
]

# ==============================
# CAMADA 1 — NORMALIZAÇÃO
# ==============================

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


def normalizar(texto):
    """
    Camada 1: limpa o texto.
    - minúsculas
    - sem acento
    - sem pontuação
    - separa juntadas comuns (oque → o que)
    """
    texto = texto.lower().strip()
    texto = remover_acentos(texto)
    texto = re.sub(r'[^\w\s]', '', texto)

    juntadas = {
        "oque": "o que",
        "oq": "o que",
        "pq": "por que",
        "pque": "por que",
        "pd": "pode",
        "vc": "voce",
        "vcs": "voces",
        "tb": "tambem",
        "tbm": "tambem",
        "blz": "beleza",
        "msg": "mensagem",
        "qdo": "quando",
        "qnto": "quanto",
        "qnt": "quanto",
        "n": "nao",
        "ñ": "nao",
        "eh": "e",
        "tah": "ta",
        "to": "estou",
        "tou": "estou",
        "tmj": "tamo junto",
        "vlw": "valeu",
        "flw": "falou",
        "kd": "cade",
        "cmg": "comigo",
        "ctg": "contigo",
        "dnv": "de novo",
        "pf": "por favor",
        "pfv": "por favor",
        "q": "que",
        "ke": "que",
    }

    palavras = texto.split()
    novas = []
    for p in palavras:
        novas.append(juntadas.get(p, p))
    return " ".join(novas)


# ==============================
# CAMADA 2 — CORREÇÃO DE DIGITAÇÃO
# ==============================

def montar_vocabulario():
    vocab = set()
    for pergunta in BASE.keys():
        for palavra in pergunta.split():
            if len(palavra) >= 2:
                vocab.add(palavra)
    return vocab


def corrigir_palavra(palavra, vocabulario):
    if palavra in vocabulario:
        return palavra

    if len(palavra) < 3:
        return palavra

    candidatos = difflib.get_close_matches(
        palavra,
        vocabulario,
        n=3,
        cutoff=0.75
    )

    for cand in candidatos:
        if abs(len(cand) - len(palavra)) <= 1:
            return cand

    return palavra


def corrigir_digitacao(texto):
    vocabulario = montar_vocabulario()
    palavras = texto.split()
    corrigidas = [corrigir_palavra(p, vocabulario) for p in palavras]
    return " ".join(corrigidas)


# ==============================
# CAMADA 3 — BUSCA POR SIMILARIDADE
# ==============================

def jaccard(texto1, texto2):
    p1 = set(texto1.split())
    p2 = set(texto2.split())
    if not p1 or not p2:
        return 0.0
    return len(p1 & p2) / len(p1 | p2)


def similaridade_letras(texto1, texto2):
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()


def busca_por_similaridade(texto):
    melhor_j = 0.0
    melhor_l = 0.0
    resp_j = None
    resp_l = None

    for pergunta_base, respostas in BASE.items():
        score_j = jaccard(texto, pergunta_base)
        score_l = similaridade_letras(texto, pergunta_base)

        if score_j > melhor_j:
            melhor_j = score_j
            resp_j = resp_j = escolher_resposta(respostas)

        if score_l > melhor_l:
            melhor_l = score_l
            resp_l = escolher_resposta(respostas)

    if melhor_j >= LIMIAR_JACCARD:
        return resp_j

    if melhor_l >= LIMIAR_DIGITACAO:
        return resp_l

    return None


def interpretar(texto):
    texto = normalizar(texto)
    texto = corrigir_digitacao(texto)
    return texto


# ==============================
# SAUDAÇÕES
# ==============================

def saudacoes(nome):
    frases = [
        f"Bom dia! Meu nome é {nome}. Como vai você?",
        f"Olá! Eu sou {nome}.",
        f"Oi! Eu sou {nome}. Como posso ajudar?"
    ]
    print(random.choice(frases))


def saudacoes_GUI(nome):
    frases = [
        f"Bom dia! Meu nome é {nome}. Como vai você?",
        f"Olá! Eu sou {nome}.",
        f"Oi! Eu sou {nome}. Como posso ajudar?"
    ]
    return random.choice(frases)


# ==============================
# RECEBER TEXTO
# ==============================

def recebeTexto():
    texto = input("Cliente: ").strip()
    texto_normalizado = normalizar(texto)

    for palavra in PALAVRAS_PROIBIDAS:
        if re.search(rf"\b{re.escape(remover_acentos(palavra.lower()))}\b",
                     texto_normalizado):
            print("Maria: Desculpe, não posso responder esse tipo de mensagem.")
            return None

    return texto


# ==============================
# CARREGAR BASE (SQLite)
# ==============================

def carregar_base():
    base = {}

    if not os.path.exists(ARQUIVO_DB):
        print("ERRO: conhecimento.db não encontrado.")
        print("Rode antes: criar_banco.py e importar_info.py")
        return base

    conexao = sqlite3.connect(ARQUIVO_DB)
    cursor = conexao.cursor()
    # Mais usadas primeiro
    cursor.execute(
        """
        SELECT pergunta, resposta, vezes_usada
        FROM conhecimento
        ORDER BY vezes_usada DESC
        """
    )

    for pergunta, resposta, _vezes in cursor.fetchall():
        if pergunta not in base:
            base[pergunta] = []
        base[pergunta].append(resposta)

    conexao.close()
    print(f"[Dona Maria] Base SQLite: {len(base)} perguntas")
    return base


BASE = carregar_base()


# ==============================
# BUSCAR RESPOSTA
# ==============================

def buscaResposta(texto):
    global BASE

    pergunta = interpretar(texto)

    if pergunta in ["tchau", "adeus", "ate logo"]:
        return "fim"

    if pergunta in BASE:
        resposta = escolher_resposta(BASE[pergunta])
        registrar_uso(pergunta, resposta)
        return resposta

    resposta = busca_por_similaridade(pergunta)
    if resposta is not None:
        # tenta achar a pergunta “vencedora” para registrar (opcional/simples: só registra se match exato)
        return resposta

    print("Maria: Não sei responder isso.")
    resposta = input("Qual deveria ser a resposta? ")
    salva_sugestao(texto, resposta)
    return "Obrigado! Aprendi uma nova resposta."


def buscaResposta_GUI(texto):
    global BASE

    pergunta = interpretar(texto)

    if pergunta in BASE:
        resposta = escolher_resposta(BASE[pergunta])
        registrar_uso(pergunta, resposta)
        return resposta

    return busca_por_similaridade(pergunta)


# ==============================
# SALVAR / EXIBIR (SQLite)
# ==============================

def salva_sugestao(pergunta, resposta):
    global BASE
    pergunta = normalizar(pergunta)
    resposta = resposta.strip()

    if pergunta not in BASE:
        BASE[pergunta] = []
    BASE[pergunta].append(resposta)

    conexao = sqlite3.connect(ARQUIVO_DB)
    cursor = conexao.cursor()
    cursor.execute(
        """
        INSERT INTO conhecimento (pergunta, resposta)
        VALUES (?, ?)
        """,
        (pergunta, resposta),
    )
    conexao.commit()
    conexao.close()


def exibeResposta(resposta, nome):
    if resposta == "fim":
        print(f"{nome}: Volte sempre!")
        return "fim"
    print(f"{nome}: {resposta}")
    return "continua"


def exibeResposta_GUI(resposta, nome):
    if resposta == "fim":
        return f"{nome}: Volte sempre!"
    return f"{nome}: {resposta}"

def registrar_uso(pergunta, resposta):
    """Soma +1 em vezes_usada no SQLite."""
    conexao = sqlite3.connect(ARQUIVO_DB)
    cursor = conexao.cursor()
    cursor.execute(
        """
        UPDATE conhecimento
        SET vezes_usada = vezes_usada + 1
        WHERE pergunta = ? AND resposta = ?
        """,
        (pergunta, resposta),
    )
    conexao.commit()
    conexao.close()

def escolher_resposta(respostas):
    """
    Se houver várias respostas, prefere a primeira da lista
    (que veio ordenada por vezes_usada DESC).
    Com 30% de chance escolhe outra, para não ficar repetitivo.
    """
    if not respostas:
        return None
    if len(respostas) == 1 or random.random() < 0.70:
        return respostas[0]
    return random.choice(respostas)
