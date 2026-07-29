#!/usr/bin/env python3
# ============================================================
#  INICIAR — sobe o Chatbot Dona Maria
#
#  Uso:
#    python iniciar.py          → abre a interface gráfica
#    python iniciar.py console  → abre no terminal
# ============================================================

import os
import sys
import runpy

# Garante que o Python trabalhe nesta pasta (acha info.txt e os .py)
PASTA = os.path.dirname(os.path.abspath(__file__))
os.chdir(PASTA)
sys.path.insert(0, PASTA)


def verificar_arquivos(modo):
    obrigatorios = ["chat.py", "info.txt"]
    if modo == "gui":
        obrigatorios.append("InterfaceGrafica.py")
    else:
        obrigatorios.append("DonaMaria.py")

    faltando = [f for f in obrigatorios if not os.path.exists(f)]
    if faltando:
        print("=" * 50)
        print("ERRO: arquivos não encontrados:")
        for f in faltando:
            print(f"  - {f}")
        print(f"\nPasta atual:\n  {PASTA}")
        print("=" * 50)
        input("Pressione Enter para sair...")
        sys.exit(1)


def main():
    modo = "gui"
    if len(sys.argv) > 1 and sys.argv[1].lower() in (
        "console", "-c", "--console", "terminal"
    ):
        modo = "console"

    verificar_arquivos(modo)

    if modo == "console":
        print("[Iniciar] Abrindo versão console...")
        runpy.run_path("DonaMaria.py", run_name="__main__")
    else:
        print("[Iniciar] Abrindo interface gráfica...")
        runpy.run_path("InterfaceGrafica.py", run_name="__main__")


if __name__ == "__main__":
    main()
