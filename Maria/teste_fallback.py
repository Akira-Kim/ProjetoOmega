"""Testa se a chave e a API do Gemini estão ok (sem abrir a GUI)."""
import fallback_ia

print("Chave encontrada?", "SIM" if fallback_ia.carregar_chave() else "NÃO")
print("Fallback disponível?", fallback_ia.fallback_disponivel())
print()
print("Perguntando: quem e o presidente do brasil...")
resp = fallback_ia.consultar_ia("Quem é o presidente do Brasil?")
print()
print("Resposta:", resp)
