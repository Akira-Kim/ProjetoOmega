import random
import re
import unicodedata
import difflib
import os

_PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_BANCO = os.path.join(_PASTA, "info.txt")

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

    # Juntadas e abreviações comuns em português (digitação rápida)
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
    """
    Junta todas as palavras que existem nas perguntas do banco.
    Isso vira o "dicionário" para corrigir erros de digitação.
    """
    vocab = set()
    for pergunta in BASE.keys():
        for palavra in pergunta.split():
            if len(palavra) >= 2:  # ignora letras soltas
                vocab.add(palavra)
    return vocab


def corrigir_palavra(palavra, vocabulario):
    """
    Se a palavra não existe no vocabulário, tenta achar
    a mais parecida (erro de digitação).
    Usa difflib — compara letra a letra.
    Só aceita candidato com tamanho parecido (evita mihora→mira).
    """
    if palavra in vocabulario:
        return palavra  # já está correta

    if len(palavra) < 3:
        return palavra  # palavras muito curtas não vale corrigir

    candidatos = difflib.get_close_matches(
        palavra,
        vocabulario,
        n=3,          # pega os 3 melhores e filtra
        cutoff=0.75
    )

    for cand in candidatos:
        # só aceita se o tamanho for parecido (diferença máxima de 2 letras)
        if abs(len(cand) - len(palavra)) <= 1:
            return cand

    return palavra  # não achou parecida boa, deixa como está


def corrigir_digitacao(texto):
    """
    Camada 2: corrige cada palavra do texto
    comparando com o vocabulário do banco.
    Ex: "pyton" → "python", "valarant" → "valorant"
    """
    vocabulario = montar_vocabulario()
    palavras = texto.split()
    corrigidas = [corrigir_palavra(p, vocabulario) for p in palavras]
    return " ".join(corrigidas)


# ==============================
# CAMADA 3 — BUSCA POR SIMILARIDADE
# ==============================

def jaccard(texto1, texto2):
    """Similaridade por palavras em comum (0.0 a 1.0)."""
    p1 = set(texto1.split())
    p2 = set(texto2.split())
    if not p1 or not p2:
        return 0.0
    return len(p1 & p2) / len(p1 | p2)


def similaridade_letras(texto1, texto2):
    """
    Similaridade letra a letra (difflib).
    Bom para frases curtas e erros de digitação.
    """
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()


def busca_por_similaridade(texto):
    """
    Camada 3: procura a pergunta mais parecida no banco.
    Usa Jaccard E similaridade de letras, cada um com seu limiar.
    """
    melhor_j = 0.0
    melhor_l = 0.0
    resp_j = None
    resp_l = None

    for pergunta_base, respostas in BASE.items():
        score_j = jaccard(texto, pergunta_base)
        score_l = similaridade_letras(texto, pergunta_base)

        if score_j > melhor_j:
            melhor_j = score_j
            resp_j = random.choice(respostas)

        if score_l > melhor_l:
            melhor_l = score_l
            resp_l = random.choice(respostas)

    # Cada score só vale se passar no SEU limiar
    if melhor_j >= LIMIAR_JACCARD:
        return resp_j

    if melhor_l >= LIMIAR_DIGITACAO:
        return resp_l

    return None


def interpretar(texto):
    """
    Pipeline completo do interpretador:
    1) normaliza
    2) corrige digitação
    3) devolve o texto pronto para buscar
    """
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
# CARREGAR BASE
# ==============================

def carregar_base():
    base = {}
    try:
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if ";" not in linha:
                    continue
                pergunta, resposta = linha.split(";", 1)
                pergunta = normalizar(pergunta)
                if pergunta not in base:
                    base[pergunta] = []
                base[pergunta].append(resposta)
    except FileNotFoundError:
        open(ARQUIVO_BANCO, "w", encoding="utf-8").close()
    return base

BASE = carregar_base()

# ==============================
# BUSCAR RESPOSTA
# ==============================

def buscaResposta(texto):
    global BASE

    # Roda o interpretador (normaliza + corrige digitação)
    pergunta = interpretar(texto)

    if pergunta in ["tchau", "adeus", "ate logo"]:
        return "fim"

    # 1) Match exato (depois da correção)
    if pergunta in BASE:
        return random.choice(BASE[pergunta])

    # 2) Match por similaridade
    resposta = busca_por_similaridade(pergunta)
    if resposta is not None:
        return resposta

    # 3) Não sabe → aprende
    print("Maria: Não sei responder isso.")
    resposta = input("Qual deveria ser a resposta? ")
    salva_sugestao(texto, resposta)
    return "Obrigado! Aprendi uma nova resposta."


def buscaResposta_GUI(texto):
    global BASE

    pergunta = interpretar(texto)

    if pergunta in BASE:
        return random.choice(BASE[pergunta])

    return busca_por_similaridade(pergunta)

# ==============================
# SALVAR / EXIBIR
# ==============================

def salva_sugestao(pergunta, resposta):
    global BASE
    pergunta = normalizar(pergunta)
    with open(ARQUIVO_BANCO, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"\n{pergunta};{resposta}")
    if pergunta not in BASE:
        BASE[pergunta] = []
    BASE[pergunta].append(resposta)


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
