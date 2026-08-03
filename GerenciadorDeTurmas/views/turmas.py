"""
views/turmas.py - Turmas, alunos, notas e coins
Parte 5 (5.1 a 5.3)
"""

import flet as ft

from models import (
    listar_turmas,
    listar_alunos,
    contar_alunos,
    criar_aluno,
    atualizar_aluno,
    desativar_aluno,
    obter_resumo_aluno,
)


def build_turmas_view(page: ft.Page) -> ft.Control:
    lista_turmas_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    painel_alunos = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    mensagem = ft.Text("", size=12)

    estado = {"turma_id": None, "turma_nome": ""}

    def mostrar_msg(texto: str, cor=ft.Colors.GREEN_400):
        mensagem.value = texto
        mensagem.color = cor
        try:
            mensagem.update()
        except Exception:
            pass

    # ---------- TURMAS ----------
    def montar_card_turma(t: dict) -> ft.Container:
        n = contar_alunos(t["id"])
        selecionada = estado["turma_id"] == t["id"]
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=8,
                        height=40,
                        bgcolor=t.get("cor") or "#4CAF50",
                        border_radius=4,
                    ),
                    ft.Column(
                        [
                            ft.Text(t["nome"], weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(
                                f"{t.get('disciplina') or '—'}  •  {n} aluno(s)",
                                size=11,
                                color=ft.Colors.GREY_400,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
            border=ft.Border.all(
                2 if selecionada else 1,
                ft.Colors.BLUE_400 if selecionada else ft.Colors.GREY_800,
            ),
            border_radius=8,
            data=t,
            on_click=on_selecionar_turma,
            ink=True,
        )

    def atualizar_lista_turmas():
        lista_turmas_col.controls.clear()
        turmas = listar_turmas()
        if not turmas:
            lista_turmas_col.controls.append(
                ft.Text("Nenhuma turma. Crie em Gerenciar.", italic=True, color=ft.Colors.GREY_500)
            )
        else:
            for t in turmas:
                lista_turmas_col.controls.append(montar_card_turma(t))
        try:
            lista_turmas_col.update()
        except Exception:
            pass

    def on_selecionar_turma(e):
        t = e.control.data
        estado["turma_id"] = t["id"]
        estado["turma_nome"] = t["nome"]
        atualizar_lista_turmas()
        carregar_alunos()
        mostrar_msg(f"Turma: {t['nome']}")

    # ---------- ALUNOS ----------
    def carregar_alunos():
        painel_alunos.controls.clear()
        tid = estado["turma_id"]
        if not tid:
            painel_alunos.controls.append(
                ft.Text("Selecione uma turma.", italic=True, color=ft.Colors.GREY_500)
            )
            try:
                painel_alunos.update()
            except Exception:
                pass
            return

        # formulario novo aluno
        tf_nome = ft.TextField(label="Nome do aluno", width=220, dense=True, text_size=13)
        tf_obs = ft.TextField(label="Obs. (opcional)", width=160, dense=True, text_size=13)

        def on_add(e):
            try:
                criar_aluno(tid, tf_nome.value or "", tf_obs.value or "")
                tf_nome.value = ""
                tf_obs.value = ""
                tf_nome.update()
                tf_obs.update()
                mostrar_msg("Aluno adicionado.")
                carregar_alunos()
                atualizar_lista_turmas()
            except Exception as ex:
                mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

        painel_alunos.controls.append(
            ft.Text(f"Alunos — {estado['turma_nome']}", size=16, weight=ft.FontWeight.W_600)
        )
        painel_alunos.controls.append(
            ft.Row(
                [
                    tf_nome,
                    tf_obs,
                    ft.ElevatedButton("Adicionar", icon=ft.Icons.PERSON_ADD, on_click=on_add),
                ],
                spacing=8,
            )
        )
        painel_alunos.controls.append(ft.Divider(height=1))

        alunos = listar_alunos(tid)
        if not alunos:
            painel_alunos.controls.append(
                ft.Text("Nenhum aluno nesta turma.", italic=True, color=ft.Colors.GREY_500)
            )
        else:
            for al in alunos:
                resumo = obter_resumo_aluno(al["id"])
                media = resumo["media_notas"]
                media_txt = f"{media:.1f}" if media is not None else "—"
                coins = resumo["total_coins"]
                qtd = resumo["qtd_registros"]

                tf_edit = ft.TextField(
                    value=al["nome"],
                    dense=True,
                    text_size=13,
                    width=180,
                    data=al["id"],
                )

                def on_salvar_nome(e, campo=tf_edit, aluno_id=al["id"]):
                    novo = (campo.value or "").strip()
                    if not novo:
                        mostrar_msg("Nome vazio.", ft.Colors.RED_400)
                        return
                    atualizar_aluno(aluno_id, nome=novo)
                    mostrar_msg("Nome atualizado.")
                    carregar_alunos()

                def on_desativar(e, aluno_id=al["id"]):
                    desativar_aluno(aluno_id)
                    mostrar_msg("Aluno desativado.", ft.Colors.ORANGE_400)
                    carregar_alunos()
                    atualizar_lista_turmas()

                painel_alunos.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        tf_edit,
                                        ft.Text(
                                            f"Media: {media_txt}  |  Coins: {coins}  |  Registros: {qtd}",
                                            size=11,
                                            color=ft.Colors.GREY_400,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.SAVE_OUTLINED,
                                    icon_size=18,
                                    tooltip="Salvar nome",
                                    on_click=on_salvar_nome,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.PERSON_OFF_OUTLINED,
                                    icon_size=18,
                                    icon_color=ft.Colors.ORANGE_400,
                                    tooltip="Desativar aluno",
                                    on_click=on_desativar,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=8,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=8,
                    )
                )

        try:
            painel_alunos.update()
        except Exception:
            pass

    # ---------- layout ----------
    # carga inicial sem update
    turmas = listar_turmas()
    if not turmas:
        lista_turmas_col.controls.append(
            ft.Text("Nenhuma turma. Crie em Gerenciar.", italic=True, color=ft.Colors.GREY_500)
        )
    else:
        for t in turmas:
            lista_turmas_col.controls.append(montar_card_turma(t))

    painel_alunos.controls.append(
        ft.Text("Selecione uma turma a esquerda.", italic=True, color=ft.Colors.GREY_500)
    )

    return ft.Column(
        [
            ft.Text("Turmas", size=26, weight=ft.FontWeight.BOLD),
            ft.Text("Alunos, notas e coins por turma.", size=13, color=ft.Colors.GREY_500),
            mensagem,
            ft.Divider(height=1),
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("Turmas", size=14, weight=ft.FontWeight.W_600),
                            lista_turmas_col,
                        ],
                        width=280,
                        expand=False,
                    ),
                    ft.VerticalDivider(width=1),
                    painel_alunos,
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        expand=True,
        spacing=8,
    )