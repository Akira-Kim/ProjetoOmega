"""
views/relatorios.py - Historico + geracao de relatorio do aluno (Gemini)
Parte 6 + Parte 7
"""

import flet as ft
from pathlib import Path

from models import (
    listar_relatorios,
    obter_relatorio,
    atualizar_relatorio,
    excluir_relatorio,
    listar_turmas,
    listar_alunos,
    obter_aula,
    obter_aluno,
    montar_contexto_aluno,
    montar_prompt_relatorio,
    criar_relatorio_aluno,
)
from utils.ai_client import ler_arquivo_modelo, gerar_com_gemini


def build_relatorios_view(page: ft.Page) -> ft.Control:
    lista_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    painel = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    mensagem = ft.Text("", size=12)

    estado = {
        "turma_id": None,
        "aluno_id": None,
        "modelo_path": None,
        "modelo_nome": None,
        "texto_gerado": "",
    }

    def mostrar_msg(texto: str, cor=ft.Colors.GREEN_400):
        mensagem.value = texto
        mensagem.color = cor
        try:
            mensagem.update()
        except Exception:
            pass

    # ---------- historico ----------
    def on_abrir(e):
        rid = e.control.data
        r = obter_relatorio(rid)
        if not r:
            mostrar_msg("Relatorio nao encontrado.", ft.Colors.RED_400)
            return

        tf_titulo = ft.TextField(
            label="Titulo",
            value=r.get("titulo") or "",
            text_size=13,
        )
        tf_conteudo = ft.TextField(
            label="Conteudo",
            value=r.get("conteudo") or "",
            multiline=True,
            min_lines=10,
            max_lines=24,
            text_size=13,
            expand=True,
        )

        info = f"Tipo: {r.get('tipo')}  |  id={r['id']}"
        if r.get("aula_id"):
            aula = obter_aula(r["aula_id"])
            if aula:
                info += f"  |  Aula: {aula.get('turma_nome')} — {aula.get('data')}"
        if r.get("aluno_id"):
            al = obter_aluno(r["aluno_id"])
            if al:
                info += f"  |  Aluno: {al.get('nome')}"
        if r.get("modelo_usado"):
            info += f"  |  Modelo: {r.get('modelo_usado')}"

        def on_salvar(ev):
            try:
                atualizar_relatorio(
                    rid,
                    titulo=tf_titulo.value or "",
                    conteudo=tf_conteudo.value or "",
                )
                mostrar_msg("Relatorio atualizado.")
                atualizar_lista()
            except Exception as ex:
                mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

        def on_excluir(ev):
            excluir_relatorio(rid)
            mostrar_msg("Relatorio excluido.", ft.Colors.ORANGE_400)
            atualizar_lista()

        painel.controls.clear()
        painel.controls.extend(
            [
                ft.Text("Editar relatorio", size=16, weight=ft.FontWeight.W_600),
                ft.Text(info, size=11, color=ft.Colors.GREY_400),
                tf_titulo,
                tf_conteudo,
                ft.Row(
                    [
                        ft.ElevatedButton("Salvar", icon=ft.Icons.SAVE, on_click=on_salvar),
                        ft.OutlinedButton(
                            "Excluir",
                            icon=ft.Icons.DELETE_OUTLINE,
                            on_click=on_excluir,
                        ),
                    ],
                    spacing=10,
                ),
            ]
        )
        try:
            painel.update()
        except Exception:
            pass

    def atualizar_lista(e=None):
        lista_col.controls.clear()
        valor = dd_filtro.value
        tipo = None
        turma_id = None
        if valor == "aula":
            tipo = "aula"
        elif valor == "aluno":
            tipo = "aluno"
        elif valor not in (None, "", "all"):
            try:
                turma_id = int(valor)
            except (TypeError, ValueError):
                turma_id = None

        rels = listar_relatorios(tipo=tipo, turma_id=turma_id)
        if not rels:
            lista_col.controls.append(
                ft.Text(
                    "Nenhum relatorio com este filtro.",
                    italic=True,
                    color=ft.Colors.GREY_500,
                )
            )
        else:
            for r in rels:
                lista_col.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    r.get("titulo") or "Sem titulo",
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                ),
                                ft.Text(
                                    f"{r.get('tipo')}  |  {r.get('data_geracao') or ''}  |  id={r['id']}",
                                    size=11,
                                    color=ft.Colors.GREY_500,
                                ),
                            ],
                            spacing=2,
                        ),
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=8,
                        data=r["id"],
                        on_click=on_abrir,
                        ink=True,
                    )
                )
        try:
            lista_col.update()
        except Exception:
            pass
        painel.controls.clear()
        painel.controls.append(
            ft.Text(
                "Selecione um relatorio ou gere um novo acima.",
                italic=True,
                color=ft.Colors.GREY_500,
            )
        )
        try:
            painel.update()
        except Exception:
            pass

    dd_filtro = ft.Dropdown(
        label="Filtro do historico",
        width=220,
        options=[
            ft.dropdown.Option(key="all", text="Todos"),
            ft.dropdown.Option(key="aula", text="So aulas"),
            ft.dropdown.Option(key="aluno", text="So alunos"),
        ],
        value="all",
    )
    for t in listar_turmas():
        dd_filtro.options.append(
            ft.dropdown.Option(key=str(t["id"]), text=f"Turma: {t['nome']}")
        )
    dd_filtro.on_change = atualizar_lista

    # ---------- geracao aluno + Gemini ----------
    dd_turma_g = ft.Dropdown(label="Turma", width=220, options=[])
    aluno_lista = ft.Column(spacing=4)
    lbl_aluno_sel = ft.Text("Nenhum aluno selecionado", size=12, color=ft.Colors.GREY_400)
    lbl_modelo = ft.Text("Nenhum modelo selecionado", size=12, color=ft.Colors.GREY_400)
    tf_caminho_modelo = ft.TextField(
        label="Caminho do modelo (.txt / .md / .docx)",
        text_size=12,
        width=420,
    )
    tf_resultado = ft.TextField(
        label="Relatorio gerado",
        multiline=True,
        min_lines=8,
        max_lines=18,
        text_size=13,
        expand=True,
    )
    tf_titulo_g = ft.TextField(label="Titulo ao salvar", text_size=13, width=280)

    def carregar_turmas_geracao():
        dd_turma_g.options = [
            ft.dropdown.Option(key=str(t["id"]), text=t["nome"]) for t in listar_turmas()
        ]
        dd_turma_g.value = None

    def selecionar_aluno(aluno_id: int, nome: str):
        estado["aluno_id"] = aluno_id
        lbl_aluno_sel.value = f"Aluno selecionado: {nome}"
        try:
            lbl_aluno_sel.update()
        except Exception:
            pass
        mostrar_msg(f"Aluno: {nome}")

    def on_turma_geracao(e=None):
        valor = dd_turma_g.value
        if not valor:
            mostrar_msg("Escolha uma turma primeiro.", ft.Colors.RED_400)
            return

        try:
            estado["turma_id"] = int(valor)
        except (TypeError, ValueError):
            mostrar_msg(f"Turma invalida: {valor}", ft.Colors.RED_400)
            return

        estado["aluno_id"] = None
        lbl_aluno_sel.value = "Nenhum aluno selecionado"
        aluno_lista.controls.clear()

        try:
            alunos = listar_alunos(estado["turma_id"])
        except Exception as ex:
            mostrar_msg(f"Erro ao listar alunos: {ex}", ft.Colors.RED_400)
            return

        mostrar_msg(f"{len(alunos)} aluno(s) na turma id={estado['turma_id']}")

        if not alunos:
            aluno_lista.controls.append(
                ft.Text(
                    "Nenhum aluno ATIVO nesta turma. Va em Turmas e confira.",
                    size=12,
                    color=ft.Colors.ORANGE_400,
                )
            )
        else:
            for al in alunos:
                aid = al["id"]
                nome = al["nome"]

                def fazer_click(e, _id=aid, _nome=nome):
                    selecionar_aluno(_id, _nome)

                aluno_lista.controls.append(
                    ft.Container(
                        content=ft.Text(nome, size=13),
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.GREY_700),
                        border_radius=6,
                        bgcolor=ft.Colors.GREY_900,
                        ink=True,
                        on_click=fazer_click,
                    )
                )

        try:
            aluno_lista.update()
            lbl_aluno_sel.update()
        except Exception:
            pass

    dd_turma_g.on_change = on_turma_geracao

    def on_usar_caminho(e):
        caminho = (tf_caminho_modelo.value or "").strip().strip('"')
        if not caminho:
            mostrar_msg("Informe o caminho do arquivo.", ft.Colors.RED_400)
            return
        if not Path(caminho).exists():
            mostrar_msg(f"Arquivo nao encontrado: {caminho}", ft.Colors.RED_400)
            return
        estado["modelo_path"] = caminho
        estado["modelo_nome"] = Path(caminho).name
        lbl_modelo.value = f"Modelo: {estado['modelo_nome']}"
        try:
            lbl_modelo.update()
        except Exception:
            pass
        mostrar_msg(f"Modelo: {estado['modelo_nome']}")

    def on_gerar(e):
        if not estado.get("modelo_path"):
            caminho = (tf_caminho_modelo.value or "").strip().strip('"')
            if caminho and Path(caminho).exists():
                estado["modelo_path"] = caminho
                estado["modelo_nome"] = Path(caminho).name

        if not estado.get("aluno_id"):
            mostrar_msg("Selecione turma e aluno.", ft.Colors.RED_400)
            return
        if not estado.get("modelo_path"):
            mostrar_msg(
                "Informe o caminho do modelo e clique em Usar caminho.",
                ft.Colors.RED_400,
            )
            return
        try:
            mostrar_msg("Gerando com Gemini...", ft.Colors.AMBER_400)
            modelo = ler_arquivo_modelo(estado["modelo_path"])
            contexto = montar_contexto_aluno(estado["aluno_id"])
            prompt = montar_prompt_relatorio(modelo, contexto)
            texto = gerar_com_gemini(prompt)
            estado["texto_gerado"] = texto
            tf_resultado.value = texto
            al = obter_aluno(estado["aluno_id"])
            tf_titulo_g.value = f"Relatorio — {al.get('nome') if al else 'aluno'}"
            tf_resultado.update()
            tf_titulo_g.update()
            mostrar_msg("Relatorio gerado! Revise e salve se quiser.")
            
        except Exception as ex:
            # fallback: mostra dados + modelo, sem IA
            try:
                modelo = ler_arquivo_modelo(estado["modelo_path"])
                contexto = montar_contexto_aluno(estado["aluno_id"])
                rascunho = (
                    f"[RASCUNHO SEM IA — Gemini indisponivel]\n"
                    f"Motivo: {ex}\n\n"
                    f"--- MODELO ---\n{modelo}\n\n"
                    f"--- DADOS DO ALUNO ---\n{contexto}\n"
                )
                tf_resultado.value = rascunho
                tf_resultado.update()
            except Exception:
                pass
            mostrar_msg(f"Erro na geracao: {ex}", ft.Colors.RED_400)

    def on_salvar_gerado(e):
        if not estado.get("aluno_id"):
            mostrar_msg("Selecione um aluno.", ft.Colors.RED_400)
            return
        texto = (tf_resultado.value or "").strip()
        if not texto:
            mostrar_msg("Nada para salvar. Gere o relatorio antes.", ft.Colors.RED_400)
            return
        try:
            rid = criar_relatorio_aluno(
                aluno_id=estado["aluno_id"],
                conteudo=texto,
                titulo=(tf_titulo_g.value or "").strip(),
                modelo_usado=estado.get("modelo_nome") or "",
                turma_id=estado.get("turma_id"),
            )
            mostrar_msg(f"Relatorio do aluno salvo (id={rid}).")
            atualizar_lista()
        except Exception as ex:
            mostrar_msg(f"Erro ao salvar: {ex}", ft.Colors.RED_400)

    def on_ver_contexto(e):
        if not estado.get("aluno_id"):
            mostrar_msg("Selecione turma e aluno.", ft.Colors.RED_400)
            return
        try:
            ctx = montar_contexto_aluno(estado["aluno_id"])
            tf_resultado.value = ctx
            tf_resultado.update()
            mostrar_msg("Contexto do aluno (sem IA). Use Gerar para chamar o Gemini.")
        except Exception as ex:
            mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

    bloco_gerar = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Gerar relatorio do aluno (Gemini)",
                    size=16,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Row(
                    [
                        dd_turma_g,
                        ft.ElevatedButton(
                            "Carregar alunos",
                            icon=ft.Icons.PEOPLE,
                            on_click=on_turma_geracao,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Text("Clique no aluno:", size=12, color=ft.Colors.GREY_400),
                aluno_lista,
                lbl_aluno_sel,
                ft.Text(
                    "Cole o caminho completo do arquivo de modelo (txt, md ou docx):",
                    size=12,
                    color=ft.Colors.GREY_400,
                ),
                ft.Row(
                    [
                        tf_caminho_modelo,
                        ft.OutlinedButton(
                            "Usar caminho",
                            icon=ft.Icons.CHECK,
                            on_click=on_usar_caminho,
                        ),
                    ],
                    spacing=8,
                ),
                lbl_modelo,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Gerar com Gemini",
                            icon=ft.Icons.AUTO_AWESOME,
                            on_click=on_gerar,
                        ),
                        ft.TextButton("Ver so os dados", on_click=on_ver_contexto),
                    ],
                    spacing=8,
                ),
                tf_titulo_g,
                tf_resultado,
                ft.ElevatedButton(
                    "Salvar relatorio do aluno",
                    icon=ft.Icons.SAVE,
                    on_click=on_salvar_gerado,
                ),
            ],
            spacing=8,
        ),
        padding=12,
        border=ft.Border.all(1, ft.Colors.GREY_800),
        border_radius=10,
    )

    carregar_turmas_geracao()
    atualizar_lista()

    return ft.Column(
        [
            ft.Text("Relatorios", size=26, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Historico de aulas/alunos e geracao com Gemini.",
                size=13,
                color=ft.Colors.GREY_500,
            ),
            mensagem,
            ft.Row(
                [
                    dd_filtro,
                    ft.TextButton("Atualizar lista", on_click=atualizar_lista),
                ]
            ),
            ft.Divider(height=1),
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("Historico", size=14, weight=ft.FontWeight.W_600),
                            lista_col,
                        ],
                        width=300,
                    ),
                    ft.VerticalDivider(width=1),
                    ft.Column(
                        [bloco_gerar, ft.Divider(), painel],
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        expand=True,
        spacing=8,
    )