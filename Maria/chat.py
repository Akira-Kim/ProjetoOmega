import random
import re
import unicodedata
import difflib
import os
import sqlite3

try:
    import fallback_ia
except ImportError:
    fallback_ia = None

_PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DB = os.path.join(_PASTA, "conhecimento.db")

LIMIAR_JACCARD = 0.45
LIMIAR_DIGITACAO = 0.72

# Se a IA responder, grava na base local automaticamente?
AUTO_APRENDER_IA = True

# ==============================
# MEMÓRIA DE CONTEXTO
# ==============================

MAX_HISTORICO = 8
historico_conversa = []   # [{"usuario", "maria", "chave"}]
ultimo_tema = None        # ex: "python", "valorant"
_ultima_chave_match = None

STOPWORDS = {
    "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
    "e", "ou", "que", "em", "no", "na", "nos", "nas", "para", "por",
    "com", "sem", "como", "qual", "quais", "quem", "onde", "quando",
    "quanto", "quantos", "quantas", "porque", "porquê",
    "meu", "minha", "seu", "sua",
    "me", "te", "se", "eu", "voce", "ele", "ela", "isso", "isto",
    "sobre", "fale", "explica", "dizer", "diz", "ai", "eh",
}


def extrair_tema(texto):
    """Pega a palavra mais 'substantiva' (em geral o assunto no final)."""
    if not texto:
        return None
    palavras = [
        p for p in normalizar(texto).split()
        if p not in STOPWORDS and len(p) >= 1
    ]
    if not palavras:
        return None
    return palavras[-1]


def atualizar_contexto(texto_usuario, chave_base, resposta):
    """Atualiza histórico e o último tema da conversa."""
    global historico_conversa, ultimo_tema

    tema = extrair_tema(chave_base) or extrair_tema(texto_usuario)
    if tema:
        ultimo_tema = tema

    historico_conversa.append({
        "usuario": texto_usuario,
        "maria": resposta,
        "chave": chave_base,
        "tema": tema,
    })
    if len(historico_conversa) > MAX_HISTORICO:
        historico_conversa.pop(0)


def limpar_contexto():
    """Zera a memória (ex.: ao dizer tchau)."""
    global historico_conversa, ultimo_tema, _ultima_chave_match
    historico_conversa = []
    ultimo_tema = None
    _ultima_chave_match = None


def tentar_expandir_contexto(pergunta_norm):
    """
    Se a frase parecer continuação ("e o de c?", "e java?"),
    monta uma pergunta completa usando o último tema.
    """
    if not pergunta_norm:
        return pergunta_norm

    # Já é uma pergunta completa o suficiente → não mexe
    if len(pergunta_norm.split()) >= 4 and not pergunta_norm.startswith("e "):
        return pergunta_norm

    # "e o presidente dos eua" / "e o dos eua" / "e o do eua"
    m = re.match(r"^e (?:o|a) (?:presidente )?(?:dos|do|da|de) (.+)$", pergunta_norm)
    if m:
        resto = m.group(1).strip()
        if resto:
            return f"quem e o presidente de {resto}"

    # "e o de c" / "e a de java" / "e o c"
    m = re.match(r"^e (?:o|a) (?:de )?(.+)$", pergunta_norm)
    if m:
        resto = m.group(1).strip()
        if resto:
            return f"o que e {resto}"

    # "e sobre valorant" / "e de python"
    m = re.match(r"^e (?:sobre|do|da|de) (.+)$", pergunta_norm)
    if m:
        resto = m.group(1).strip()
        if resto:
            return f"o que e {resto}"

    # "e java" / "e html" (curto)
    m = re.match(r"^e (.+)$", pergunta_norm)
    if m and len(pergunta_norm.split()) <= 3:
        resto = m.group(1).strip()
        if resto and resto not in STOPWORDS:
            return f"o que e {resto}"

    # "me fala mais" / "e mais" / "continua" → tenta "o que e {tema}"
    if pergunta_norm in ("me fala mais", "fale mais", "e mais", "continua", "mais"):
        if ultimo_tema:
            return f"o que e {ultimo_tema}"

    return pergunta_norm


def preparar_pergunta(texto):
    """
    Pipeline:
    1) interpretar (normalizar + digitação)
    2) expandir com contexto da conversa
    3) interpretar de novo (se expandiu)
    """
    pergunta = interpretar(texto)
    expandida = tentar_expandir_contexto(pergunta)
    if expandida != pergunta:
        pergunta = interpretar(expandida)
    return pergunta


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
    return " ".join(juntadas.get(p, p) for p in palavras)


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


# Palavras comuns do PT que NÃO devem ser "corrigidas" pelo difflib
# (ex.: "dos" virava "dois" por causa de "dois mais dois" no banco)
PALAVRAS_PROTEGIDAS = {
    "dos", "das", "do", "da", "de", "em", "no", "na", "nos", "nas",
    "um", "uma", "uns", "umas", "ao", "aos", "pelo", "pela", "pelos", "pelas",
    "eu", "tu", "ele", "ela", "nos", "vos", "eles", "elas",
    "meu", "minha", "teu", "tua", "seu", "sua",
    "mais", "menos", "muito", "pouco", "bem", "mal",
    "presidente", "brasil", "eua", "estados", "unidos",
}

def corrigir_palavra(palavra, vocabulario):
    if palavra in vocabulario:
        return palavra
    if palavra in PALAVRAS_PROTEGIDAS:
        return palavra
    if len(palavra) < 3:
        return palavra

    candidatos = difflib.get_close_matches(
        palavra, vocabulario, n=3, cutoff=0.75
    )
    for cand in candidatos:
        if abs(len(cand) - len(palavra)) <= 1:
            return cand
    return palavra


def corrigir_digitacao(texto):
    vocabulario = montar_vocabulario()
    return " ".join(corrigir_palavra(p, vocabulario) for p in texto.split())


# ==============================
# CAMADA 3 — BUSCA POR SIMILARIDADE
# ==============================

def palavras_conteudo(texto):
    """Remove stopwords para comparar o que importa (python, brasil, mira...)."""
    return set(
        p for p in texto.split()
        if p not in STOPWORDS and len(p) >= 1
    )


def jaccard(texto1, texto2):
    """
    Similaridade por palavras de CONTEÚDO (sem o/que/e/de...).
    Evita que "o que e python" e "o que e java" pareçam iguais.
    """
    p1 = palavras_conteudo(texto1)
    p2 = palavras_conteudo(texto2)
    if not p1 or not p2:
        return 0.0
    return len(p1 & p2) / len(p1 | p2)


def similaridade_letras(texto1, texto2):
    """
    Compara letra a letra só o miolo (sem stopwords).
    Assim o prefixo "o que e " não engana o score.
    """
    c1 = " ".join(sorted(palavras_conteudo(texto1)))
    c2 = " ".join(sorted(palavras_conteudo(texto2)))
    if not c1 or not c2:
        return 0.0
    return difflib.SequenceMatcher(None, c1, c2).ratio()


def escolher_resposta(respostas):
    if not respostas:
        return None
    if len(respostas) == 1 or random.random() < 0.70:
        return respostas[0]
    return random.choice(respostas)


def busca_por_similaridade(texto):
    """Procura pergunta parecida e registra uso da chave vencedora."""
    global _ultima_chave_match

    melhor_j = 0.0
    melhor_l = 0.0
    pergunta_j = None
    pergunta_l = None
    resp_j = None
    resp_l = None

    for pergunta_base, respostas in BASE.items():
        score_j = jaccard(texto, pergunta_base)
        score_l = similaridade_letras(texto, pergunta_base)

        if score_j > melhor_j:
            melhor_j = score_j
            pergunta_j = pergunta_base
            resp_j = escolher_resposta(respostas)

        if score_l > melhor_l:
            melhor_l = score_l
            pergunta_l = pergunta_base
            resp_l = escolher_resposta(respostas)

    if melhor_j >= LIMIAR_JACCARD and resp_j is not None:
        _ultima_chave_match = pergunta_j
        registrar_uso(pergunta_j, resp_j)
        return resp_j

    # Similaridade de letras só vale se houver alguma palavra de conteúdo em comum
    # (evita "presidente do brasil" ≈ "descobriu o brasil" só por "brasil")
    if melhor_l >= LIMIAR_DIGITACAO and resp_l is not None:
        if palavras_conteudo(texto) & palavras_conteudo(pergunta_l):
            # precisa mais do que 1 stop-ish match: se a interseção for só 1 palavra
            # genérica curta, exige score bem alto
            inter = palavras_conteudo(texto) & palavras_conteudo(pergunta_l)
            if len(inter) >= 2 or melhor_l >= 0.85:
                _ultima_chave_match = pergunta_l
                registrar_uso(pergunta_l, resp_l)
                return resp_l

    return None


def interpretar(texto):
    return corrigir_digitacao(normalizar(texto))


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
# REGISTRAR USO + SALVAR
# ==============================

def registrar_uso(pergunta, resposta):
    if not pergunta or not resposta:
        return
    try:
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
    except Exception:
        pass


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
        INSERT INTO conhecimento (pergunta, resposta, vezes_usada)
        VALUES (?, ?, 0)
        """,
        (pergunta, resposta),
    )
    conexao.commit()
    conexao.close()



def tentar_fallback_ia(texto_original, pergunta_preparada=None):
    """
    Quando a base local falha, tenta a IA externa.
    Se AUTO_APRENDER_IA e a IA responder, salva no SQLite.
    pergunta_preparada: versão já expandida pelo contexto (melhor para a IA).
    """
    if fallback_ia is None:
        return None

    historico = historico_conversa if historico_conversa else None
    # Prefere a pergunta expandida ("quem e o presidente de eua")
    pergunta_para_ia = pergunta_preparada or texto_original
    resposta_ia = fallback_ia.consultar_ia(pergunta_para_ia, historico)

    if not resposta_ia:
        return None

    # Aprende com a formulação preparada (mais útil na próxima busca)
    chave_aprender = normalizar(pergunta_para_ia)
    if AUTO_APRENDER_IA:
        salva_sugestao(chave_aprender, resposta_ia)

    atualizar_contexto(texto_original, chave_aprender, resposta_ia)
    return resposta_ia


# ==============================
# BUSCAR RESPOSTA (com contexto)
# ==============================

def buscaResposta(texto):
    global BASE, _ultima_chave_match

    _ultima_chave_match = None
    pergunta = preparar_pergunta(texto)

    if pergunta in ["tchau", "adeus", "ate logo"]:
        limpar_contexto()
        return "fim"

    # 1) Match exato
    if pergunta in BASE:
        resposta = escolher_resposta(BASE[pergunta])
        registrar_uso(pergunta, resposta)
        atualizar_contexto(texto, pergunta, resposta)
        return resposta

    # 2) Similaridade
    resposta = busca_por_similaridade(pergunta)
    if resposta is not None:
        atualizar_contexto(texto, _ultima_chave_match, resposta)
        return resposta

    # 3) Fallback de IA (se configurado)
    resposta = tentar_fallback_ia(texto, pergunta)
    if resposta is not None:
        return resposta

    # 4) Não sabe → aprende com o usuário
    print("Maria: Não sei responder isso.")
    resposta = input("Qual deveria ser a resposta? ")
    salva_sugestao(texto, resposta)
    atualizar_contexto(texto, normalizar(texto), resposta)
    return "Obrigado! Aprendi uma nova resposta."


def buscaResposta_GUI(texto):
    global BASE, _ultima_chave_match

    _ultima_chave_match = None
    pergunta = preparar_pergunta(texto)

    # 1) Match exato
    if pergunta in BASE:
        resposta = escolher_resposta(BASE[pergunta])
        registrar_uso(pergunta, resposta)
        atualizar_contexto(texto, pergunta, resposta)
        return resposta

    # 2) Similaridade
    resposta = busca_por_similaridade(pergunta)
    if resposta is not None:
        atualizar_contexto(texto, _ultima_chave_match, resposta)
        return resposta

    # 3) Fallback de IA
    return tentar_fallback_ia(texto, pergunta)


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
