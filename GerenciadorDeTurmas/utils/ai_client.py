"""
utils/ai_client.py - Leitura da chave e chamada ao Gemini
"""

from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = ROOT / "keys" / "gemini_key.txt"

# modelo estavel da API gratuita (pode mudar no futuro)
GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


def carregar_chave_gemini() -> str:
    if not KEY_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo de chave nao encontrado: {KEY_FILE}\n"
            "Crie keys/gemini_key.txt e cole a API key do Google AI Studio."
        )
    chave = KEY_FILE.read_text(encoding="utf-8").strip()
    if not chave or chave == "COLE_SUA_CHAVE_AQUI":
        raise ValueError("Chave Gemini vazia. Edite keys/gemini_key.txt")
    return chave


def gerar_com_gemini(prompt: str, timeout: float = 60.0) -> str:
    """Envia o prompt ao Gemini. Em caso de cota/erro, levanta RuntimeError com texto claro."""
    chave = carregar_chave_gemini()
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 4096,
        },
    }
    with httpx.Client(timeout=timeout) as client:
        r = client.post(
            GEMINI_URL,
            params={"key": chave},
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        if r.status_code == 429:
            raise RuntimeError(
                "Cota gratuita do Gemini esgotada (HTTP 429). "
                "Use 'Ver so os dados', aguarde o reset da cota, "
                "troque o modelo em ai_client.py ou use outra API key."
            )
        if r.status_code == 403:
            raise RuntimeError(
                "Acesso negado (HTTP 403). Confira a API key em keys/gemini_key.txt "
                "e se a Generative Language API esta ativa no Google AI Studio."
            )
        if r.status_code != 200:
            raise RuntimeError(f"Gemini HTTP {r.status_code}: {r.text[:400]}")

        data = r.json()

    try:
        parts = data["candidates"][0]["content"]["parts"]
        textos = [p.get("text", "") for p in parts if "text" in p]
        texto = "\n".join(textos).strip()
        if not texto:
            raise RuntimeError("Resposta vazia do Gemini.")
        return texto
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Formato inesperado da resposta Gemini: {data}") from e


def ler_arquivo_modelo(caminho: str) -> str:
    """Le .txt, .md, .docx ou outro texto simples."""
    path = Path(caminho)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

    suf = path.suffix.lower()
    if suf in (".txt", ".md", ".markdown", ".csv", ".log"):
        return path.read_text(encoding="utf-8", errors="replace")

    if suf in (".docx",):
        try:
            from docx import Document
        except ImportError:
            raise RuntimeError("Instale python-docx: pip install python-docx")
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    # tentativa generica
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise RuntimeError(
            f"Nao foi possivel ler '{suf}'. Use .txt, .md ou .docx. Detalhe: {e}"
        )