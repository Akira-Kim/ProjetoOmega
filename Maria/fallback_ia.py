# ============================================================
#  Fallback de IA — Google Gemini (API gratuita)
#
#  Chave: https://aistudio.google.com/apikey
#  Arquivo: api_key.txt (uma linha) ou env GEMINI_API_KEY
# ============================================================

import json
import os
import urllib.request
import urllib.error
import urllib.parse

_PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_CHAVE = os.path.join(_PASTA, "api_key.txt")

# Modelos na ordem de preferência (os que costumam funcionar no free tier)
# gemini-flash-latest = alias que o Google mantém atualizado
MODELOS = [
    "gemini-flash-latest",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
]

FALLBACK_ATIVO = True

# Tamanho máximo da resposta (antes estava baixo e cortava o texto)
MAX_TOKENS = 1024


def carregar_chave():
    for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        chave = os.environ.get(var, "").strip()
        if chave:
            return chave

    if os.path.exists(ARQUIVO_CHAVE):
        with open(ARQUIVO_CHAVE, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith("#"):
                    return linha
    return None


def listar_modelos():
    """Lista modelos da sua conta que aceitam generateContent."""
    chave = carregar_chave()
    if not chave:
        print("Sem chave.")
        return []
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models"
        f"?key={urllib.parse.quote(chave)}"
    )
    disponiveis = []
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
        print("Modelos com generateContent:")
        for m in dados.get("models", []):
            metodos = m.get("supportedGenerationMethods") or []
            if "generateContent" in metodos:
                nome = m.get("name", "").replace("models/", "")
                print(" -", nome)
                disponiveis.append(nome)
    except Exception as e:
        print("Falha ao listar modelos:", e)
    return disponiveis


def _montar_prompt(pergunta, historico=None):
    partes = [
        "Você é a Maria, assistente em português do Brasil.",
        "Regras de resposta:",
        "- Responda de forma completa e clara (não corte no meio da frase).",
        "- Use entre 2 e 5 frases curtas, o suficiente para responder bem.",
        "- Não use markdown, listas longas nem títulos.",
        "- Se não souber com certeza, diga isso com honestidade.",
        "",
    ]
    if historico:
        partes.append("Conversa recente:")
        for item in historico[-4:]:
            if item.get("usuario"):
                partes.append(f"Usuário: {item['usuario']}")
            if item.get("maria"):
                partes.append(f"Maria: {item['maria']}")
        partes.append("")
    partes.append(f"Pergunta atual do usuário: {pergunta}")
    return "\n".join(partes)


def _chamar_modelo(modelo, chave, prompt):
    corpo = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": MAX_TOKENS,
        },
    }
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent?key={urllib.parse.quote(chave)}"
    )
    dados = json.dumps(corpo).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=dados,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _extrair_texto(resultado):
    """Lê o texto da resposta Gemini, inclusive se vier em várias parts."""
    candidatos = resultado.get("candidates") or []
    if not candidatos:
        return None

    cand = candidatos[0]

    # Aviso se a resposta foi cortada por limite de tokens
    razao = cand.get("finishReason") or cand.get("finish_reason")
    if razao and str(razao).upper() in ("MAX_TOKENS", "LENGTH"):
        print("[Fallback IA] Aviso: resposta pode ter sido cortada (MAX_TOKENS).")

    partes = cand.get("content", {}).get("parts") or []
    textos = [p.get("text", "") for p in partes if isinstance(p, dict) and p.get("text")]
    texto = "\n".join(textos).strip()
    return texto if texto else None


def consultar_ia(pergunta, historico=None):
    if not FALLBACK_ATIVO:
        print("[Fallback IA] Desativado (FALLBACK_ATIVO = False)")
        return None

    chave = carregar_chave()
    if not chave:
        print("[Fallback IA] Sem chave. Crie api_key.txt ou defina GEMINI_API_KEY.")
        return None

    prompt = _montar_prompt(pergunta, historico)

    for modelo in MODELOS:
        try:
            resultado = _chamar_modelo(modelo, chave, prompt)
            texto = _extrair_texto(resultado)
            if texto:
                print(f"[Fallback IA] OK via {modelo}")
                return texto
            print(f"[Fallback IA] {modelo}: resposta vazia")
        except urllib.error.HTTPError as e:
            detalhe = ""
            try:
                detalhe = e.read().decode("utf-8", errors="replace")[:250]
            except Exception:
                pass
            if e.code == 429:
                print(f"[Fallback IA] {modelo}: cota esgotada (429). Tentando próximo...")
            elif e.code == 404:
                print(f"[Fallback IA] {modelo}: não encontrado (404). Tentando próximo...")
            else:
                print(f"[Fallback IA] {modelo} falhou: HTTP {e.code}: {detalhe}")
        except Exception as e:
            print(f"[Fallback IA] {modelo} falhou: {type(e).__name__}: {e}")

    print("[Fallback IA] Nenhum modelo respondeu.")
    return None


def fallback_disponivel():
    return FALLBACK_ATIVO and carregar_chave() is not None


if __name__ == "__main__":
    print("=== Modelos disponíveis ===")
    listar_modelos()
    print()
    print("=== Teste ===")
    r = consultar_ia("Quem é o presidente do Brasil? Responda de forma completa.")
    print("Resposta:", r)
