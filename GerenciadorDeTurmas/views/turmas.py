"""
views/turmas.py - Turmas, alunos, historico e edicao
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
    obter_aluno,
    listar_historico_aluno,
    atualizar_turma,
    obter_turma,
    salvar_registro_aula,
)


def build_turmas_view(page: ft.Page) -> ft.Control:
    lista_turmas_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    painel = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    mensagem = ft.Text("", size=12)

    estado = {"turma_id": None, "turma_nome": "", "aluno_id": None}

    def mostrar_msg(texto: str, cor=ft.Colors.GREEN_400):
        mensagem.value = texto
        mensagem.color = cor
        try:
            mensagem.update()
        except Exception:
            pass

    # ---------- cards de turma ----------
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
        estado["aluno_id"] = None
        atualizar_lista_turmas()
        mostrar_painel_turma()

    # ---------- painel da turma (editar nome/materia + lista alunos) ----------
    def mostrar_painel_turma():
        painel.controls.clear()
        tid = estado["turma_id"]
        if not tid:
            painel.controls.append(
                ft.Text("Selecione uma turma.", italic=True, color=ft.Colors.GREY_500)
            )
            try:
                painel.update()
            except Exception:
                pass
            return

        t = obter_turma(tid) or {}
        tf_nome_turma = ft.TextField(
            label="Nome da turma",
            value=t.get("nome") or "",
            text_size=13,
            width=220,
        )
        tf_disc = ft.TextField(
            label="Disciplina / materia",
            value=t.get("disciplina") or "",
            text_size=13,
            width=220,
        )

        def on_salvar_turma(e):
            try:
                atualizar_turma(
                    tid,
                    nome=(tf_nome_turma.value or "").strip() or t.get("nome"),
                    disciplina=(tf_disc.value or "").strip(),
                )
                estado["turma_nome"] = tf_nome_turma.value or estado["turma_nome"]
                mostrar_msg("Turma atualizada.")
                atualizar_lista_turmas()
                mostrar_painel_turma()
            except Exception as ex:
                mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

        # novo aluno
        tf_nome_aluno = ft.TextField(label="Nome do aluno", width=200, text_size=13)
        tf_obs_aluno = ft.TextField(label="Obs. (opcional)", width=160, text_size=13)

        def on_add_aluno(e):
            try:
                criar_aluno(tid, tf_nome_aluno.value or "", tf_obs_aluno.value or "")
                tf_nome_aluno.value = ""
                tf_obs_aluno.value = ""
                tf_nome_aluno.update()
                tf_obs_aluno.update()
                mostrar_msg("Aluno adicionado.")
                atualizar_lista_turmas()
                mostrar_painel_turma()
            except Exception as ex:
                mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

        painel.controls.append(
            ft.Text(f"Turma: {estado['turma_nome']}", size=16, weight=ft.FontWeight.W_600)
        )
        painel.controls.append(ft.Text("Editar turma", size=13, weight=ft.FontWeight.W_500))
        painel.controls.append(ft.Row([tf_nome_turma, tf_disc], spacing=8))
        painel.controls.append(
            ft.ElevatedButton("Salvar turma", icon=ft.Icons.SAVE, on_click=on_salvar_turma)
        )
        painel.controls.append(ft.Divider(height=1))
        painel.controls.append(ft.Text("Adicionar aluno", size=13, weight=ft.FontWeight.W_500))
        painel.controls.append(
            ft.Row(
                [
                    tf_nome_aluno,
                    tf_obs_aluno,
                    ft.ElevatedButton("Adicionar", icon=ft.Icons.PERSON_ADD, on_click=on_add_aluno),
                ],
                spacing=8,
            )
        )
        painel.controls.append(ft.Divider(height=1))
        painel.controls.append(ft.Text("Alunos (clique para abrir a ficha)", size=13, weight=ft.FontWeight.W_500))

        alunos = listar_alunos(tid)
        if not alunos:
            painel.controls.append(
                ft.Text("Nenhum aluno nesta turma.", italic=True, color=ft.Colors.GREY_500)
            )
        else:
            for al in alunos:
                resumo = obter_resumo_aluno(al["id"])
                media = resumo["media_notas"]
                media_txt = f"{media:.1f}" if media is not None else "—"
                coins = resumo["total_coins"]
                qtd = resumo["qtd_registros"]

                painel.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(al["nome"], size=13, weight=ft.FontWeight.W_500),
                                        ft.Text(
                                            f"Media: {media_txt}  |  Coins: {coins}  |  Registros: {qtd}",
                                            size=11,
                                            color=ft.Colors.GREY_400,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=ft.Colors.GREY_500),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=8,
                        data=al["id"],
                        on_click=on_abrir_aluno,
                        ink=True,
                    )
                )

        try:
            painel.update()
        except Exception:
            pass

    # ---------- ficha do aluno ----------
    def on_abrir_aluno(e):
        estado["aluno_id"] = e.control.data
        mostrar_ficha_aluno()

    def mostrar_ficha_aluno():
        painel.controls.clear()
        aluno_id = estado["aluno_id"]
        al = obter_aluno(aluno_id)
        if not al:
            mostrar_msg("Aluno nao encontrado.", ft.Colors.RED_400)
            mostrar_painel_turma()
            return

        resumo = obter_resumo_aluno(aluno_id)
        media = resumo["media_notas"]
        media_txt = f"{media:.1f}" if media is not None else "—"
        total_coins = resumo["total_coins"]

        tf_nome = ft.TextField(label="Nome", value=al.get("nome") or "", text_size=13, width=240)
        tf_obs = ft.TextField(
            label="Observacao geral do aluno",
            value=al.get("observacao") or "",
            text_size=13,
            multiline=True,
            min_lines=2,
            max_lines=4,
            width=320,
        )

        def on_salvar_aluno(e):
            try:
                atualizar_aluno(
                    aluno_id,
                    nome=(tf_nome.value or "").strip() or al.get("nome"),
                    observacao=tf_obs.value or "",
                )
                mostrar_msg("Dados do aluno salvos.")
                atualizar_lista_turmas()
                mostrar_ficha_aluno()
            except Exception as ex:
                mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

        def on_desativar(e):
            desativar_aluno(aluno_id)
            mostrar_msg("Aluno desativado.", ft.Colors.ORANGE_400)
            estado["aluno_id"] = None
            atualizar_lista_turmas()
            mostrar_painel_turma()

        def on_voltar(e):
            estado["aluno_id"] = None
            mostrar_painel_turma()

        painel.controls.extend(
            [
                ft.Row(
                    [
                        ft.TextButton("Voltar", icon=ft.Icons.ARROW_BACK, on_click=on_voltar),
                        ft.Text("Ficha do aluno", size=16, weight=ft.FontWeight.W_600),
                    ]
                ),
                ft.Text(
                    f"Media: {media_txt}  |  Coins totais: {total_coins}  |  Registros: {resumo['qtd_registros']}",
                    size=12,
                    color=ft.Colors.GREY_400,
                ),
                tf_nome,
                tf_obs,
                ft.Row(
                    [
                        ft.ElevatedButton("Salvar aluno", icon=ft.Icons.SAVE, on_click=on_salvar_aluno),
                        ft.OutlinedButton(
                            "Desativar",
                            icon=ft.Icons.PERSON_OFF_OUTLINED,
                            on_click=on_desativar,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1),
                ft.Text("Historico aula a aula", size=14, weight=ft.FontWeight.W_600),
            ]
        )

        historico = listar_historico_aluno(aluno_id)
        if not historico:
            painel.controls.append(
                ft.Text(
                    "Nenhum registro ainda. Lance nota/coins no detalhe da aula (Semana).",
                    italic=True,
                    color=ft.Colors.GREY_500,
                    size=12,
                )
            )
        else:
            for h in historico:
                tf_nota = ft.TextField(
                    label="Nota",
                    value="" if h["nota_dia"] is None else str(h["nota_dia"]),
                    width=70,
                    text_size=12,
                )
                tf_coins = ft.TextField(
                    label="Coins",
                    value=str(h.get("coins") if h.get("coins") is not None else 0),
                    width=70,
                    text_size=12,
                )
                tf_analise = ft.TextField(
                    label="Analise / comentario",
                    value=h.get("analise") or "",
                    text_size=12,
                    expand=True,
                    multiline=True,
                    min_lines=1,
                    max_lines=3,
                )

                def fazer_salvar_reg(e, aula_id=h["aula_id"], aluno=aluno_id, n=tf_nota, c=tf_coins, a=tf_analise):
                    try:
                        nota_raw = (n.value or "").strip()
                        coins_raw = (c.value or "0").strip()
                        nota = float(nota_raw.replace(",", ".")) if nota_raw else None
                        try:
                            coins = int(float(coins_raw)) if coins_raw else 0
                        except ValueError:
                            coins = 0
                        salvar_registro_aula(
                            aula_id,
                            aluno,
                            nota_dia=nota,
                            coins=coins,
                            analise=a.value or "",
                        )
                        mostrar_msg(f"Registro de {h['data_aula']} atualizado.")
                        mostrar_ficha_aluno()
                    except Exception as ex:
                        mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

                painel.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"{h['data_aula']}  •  {h.get('turma_nome') or ''}  •  {h.get('status_aula') or ''}",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Row([tf_nota, tf_coins], spacing=6),
                                tf_analise,
                                ft.TextButton(
                                    "Salvar este registro",
                                    icon=ft.Icons.SAVE_OUTLINED,
                                    on_click=fazer_salvar_reg,
                                ),
                            ],
                            spacing=4,
                        ),
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=8,
                    )
                )

        try:
            painel.update()
        except Exception:
            pass

    # ---------- carga inicial ----------
    turmas = listar_turmas()
    if not turmas:
        lista_turmas_col.controls.append(
            ft.Text("Nenhuma turma. Crie em Gerenciar.", italic=True, color=ft.Colors.GREY_500)
        )
    else:
        for t in turmas:
            lista_turmas_col.controls.append(montar_card_turma(t))

    painel.controls.append(
        ft.Text("Selecione uma turma a esquerda.", italic=True, color=ft.Colors.GREY_500)
    )

    return ft.Column(
        [
            ft.Text("Turmas", size=26, weight=ft.FontWeight.BOLD),
            ft.Text("Editar turma, alunos e historico aula a aula.", size=13, color=ft.Colors.GREY_500),
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
                    ),
                    ft.VerticalDivider(width=1),
                    painel,
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        expand=True,
        spacing=8,
    )