"""
views/gerenciar.py - Cadastro de turmas, eventos, aulas e backup
"""

import flet as ft
from datetime import date, timedelta

from models import (
    listar_turmas,
    criar_turma,
    excluir_turma,
    listar_aulas_turma,
    listar_eventos,
    criar_evento,
    excluir_evento,
    regenerar_todas_turmas_ativas,
    remarcar_aula,
)
from utils.calendar_helpers import dias_semana_para_texto, parse_dias_semana
from utils.backup import fazer_backup


def build_gerenciar_view(page: ft.Page) -> ft.Control:
    lista_turmas_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    lista_eventos_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=180)
    painel_aulas = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
    mensagem = ft.Text("", size=13)

    turma_selecionada_id = {"id": None}

    # ---------- formulario turma ----------
    tf_nome = ft.TextField(label="Nome da turma", width=260)
    tf_disciplina = ft.TextField(label="Disciplina / Materia", width=260)

    dias_checks = {
        0: ft.Checkbox(label="Seg", value=False),
        1: ft.Checkbox(label="Ter", value=False),
        2: ft.Checkbox(label="Qua", value=False),
        3: ft.Checkbox(label="Qui", value=False),
        4: ft.Checkbox(label="Sex", value=False),
        5: ft.Checkbox(label="Sab", value=False),
        6: ft.Checkbox(label="Dom", value=False),
    }

    tf_inicio = ft.TextField(
        label="Inicio (AAAA-MM-DD)",
        width=160,
        value=date.today().isoformat(),
    )
    tf_fim = ft.TextField(
        label="Fim (AAAA-MM-DD)",
        width=160,
        value=(date.today() + timedelta(days=180)).isoformat(),
    )

    # ---------- formulario evento ----------
    tf_ev_titulo = ft.TextField(label="Titulo do evento", width=220)
    tf_ev_data = ft.TextField(
        label="Data (AAAA-MM-DD)",
        width=150,
        value=date.today().isoformat(),
    )
    dd_ev_tipo = ft.Dropdown(
        label="Tipo",
        width=150,
        options=[
            ft.dropdown.Option(key="feriado", text="Feriado"),
            ft.dropdown.Option(key="recesso", text="Recesso"),
            ft.dropdown.Option(key="evento", text="Evento"),
            ft.dropdown.Option(key="reposicao", text="Reposicao"),
            ft.dropdown.Option(key="monitoria", text="Monitoria"),
        ],
        value="recesso",
    )

    def mostrar_msg(texto: str, cor=ft.Colors.GREEN_400):
        mensagem.value = texto
        mensagem.color = cor
        try:
            mensagem.update()
        except Exception:
            pass

    def montar_card_turma(t: dict) -> ft.Container:
        dias_txt = dias_semana_para_texto(parse_dias_semana(t["dias_semana"]))
        aulas = listar_aulas_turma(t["id"])
        selecionada = turma_selecionada_id["id"] == t["id"]

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=8,
                        height=44,
                        bgcolor=t.get("cor") or "#4CAF50",
                        border_radius=4,
                    ),
                    ft.Column(
                        [
                            ft.Text(t["nome"], weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(
                                f"{t.get('disciplina') or '—'} • {dias_txt} • {len(aulas)} aulas",
                                size=11,
                                color=ft.Colors.GREY_400,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        icon_size=18,
                        tooltip="Excluir",
                        data=t["id"],
                        on_click=on_excluir_turma,
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
            data=t["id"],
            on_click=on_selecionar_turma,
            ink=True,
        )

    def atualizar_lista_turmas():
        lista_turmas_col.controls.clear()
        turmas = listar_turmas()
        if not turmas:
            lista_turmas_col.controls.append(
                ft.Text("Nenhuma turma cadastrada.", italic=True, color=ft.Colors.GREY_500)
            )
        else:
            for t in turmas:
                lista_turmas_col.controls.append(montar_card_turma(t))
        try:
            lista_turmas_col.update()
        except Exception:
            pass

    def atualizar_lista_eventos():
        lista_eventos_col.controls.clear()
        eventos = listar_eventos()
        if not eventos:
            lista_eventos_col.controls.append(
                ft.Text("Nenhum evento.", italic=True, color=ft.Colors.GREY_500, size=12)
            )
        else:
            for ev in eventos:
                cor = ev.get("cor") or "#9C27B0"
                lista_eventos_col.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(width=6, height=28, bgcolor=cor, border_radius=3),
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"{ev['data']} — {ev['titulo']}",
                                            size=12,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        ft.Text(ev["tipo"], size=10, color=ft.Colors.GREY_500),
                                    ],
                                    spacing=0,
                                    expand=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_size=14,
                                    icon_color=ft.Colors.RED_300,
                                    data=ev["id"],
                                    on_click=on_excluir_evento,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=6,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=6,
                    )
                )
        try:
            lista_eventos_col.update()
        except Exception:
            pass

    def carregar_aulas_turma(turma_id: int):
        painel_aulas.controls.clear()
        aulas = listar_aulas_turma(turma_id)
        if not aulas:
            painel_aulas.controls.append(
                ft.Text("Nenhuma aula gerada.", italic=True, color=ft.Colors.GREY_500)
            )
        else:
            painel_aulas.controls.append(
                ft.Text(f"{len(aulas)} aulas", size=13, color=ft.Colors.GREY_400)
            )
            for a in aulas:
                status = a.get("status") or "planejada"
                cor_status = {
                    "planejada": ft.Colors.GREY_400,
                    "estudada": ft.Colors.AMBER_400,
                    "dada": ft.Colors.GREEN_400,
                    "cancelada": ft.Colors.RED_300,
                    "adiada": ft.Colors.ORANGE_300,
                }.get(status, ft.Colors.GREY_400)

                tf_data = ft.TextField(
                    value=a["data"],
                    width=120,
                    dense=True,
                    text_size=12,
                    data=a["id"],
                )

                def fazer_remarcar(e, campo=tf_data, aula_id=a["id"]):
                    nova_data = (campo.value or "").strip()
                    try:
                        msg = remarcar_aula(aula_id, nova_data)
                        mostrar_msg(msg)
                        carregar_aulas_turma(turma_selecionada_id["id"])
                        atualizar_lista_turmas()
                    except Exception as ex:
                        mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

                painel_aulas.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(a["data"], width=95, size=12),
                                ft.Text(status, size=11, color=cor_status, width=70),
                                tf_data,
                                ft.IconButton(
                                    icon=ft.Icons.SAVE_OUTLINED,
                                    icon_size=16,
                                    tooltip="Salvar nova data",
                                    on_click=fazer_remarcar,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=4,
                    )
                )
        try:
            painel_aulas.update()
        except Exception:
            pass

    # ---------- handlers ----------
    def on_selecionar_turma(e):
        turma_id = e.control.data
        turma_selecionada_id["id"] = turma_id
        atualizar_lista_turmas()
        carregar_aulas_turma(turma_id)
        mostrar_msg(
            f"Turma {turma_id} selecionada — edite as datas a direita se quiser remarcar."
        )

    def on_excluir_turma(e):
        excluir_turma(e.control.data)
        if turma_selecionada_id["id"] == e.control.data:
            turma_selecionada_id["id"] = None
            painel_aulas.controls.clear()
            painel_aulas.controls.append(
                ft.Text("Selecione uma turma.", italic=True, color=ft.Colors.GREY_500)
            )
            try:
                painel_aulas.update()
            except Exception:
                pass
        mostrar_msg("Turma excluida.", ft.Colors.ORANGE_400)
        atualizar_lista_turmas()

    def on_salvar_turma(e):
        nome = (tf_nome.value or "").strip()
        if not nome:
            mostrar_msg("Informe o nome da turma.", ft.Colors.RED_400)
            return
        dias = [str(d) for d, cb in dias_checks.items() if cb.value]
        if not dias:
            mostrar_msg("Selecione pelo menos um dia.", ft.Colors.RED_400)
            return
        try:
            tid = criar_turma(
                nome=nome,
                disciplina=(tf_disciplina.value or "").strip(),
                dias_semana=",".join(dias),
                data_inicio=tf_inicio.value.strip(),
                data_fim=tf_fim.value.strip(),
            )
            tf_nome.value = ""
            tf_disciplina.value = ""
            for cb in dias_checks.values():
                cb.value = False
            tf_nome.update()
            tf_disciplina.update()
            for cb in dias_checks.values():
                cb.update()
            mostrar_msg(f"Turma criada (id={tid}) e aulas geradas!")
            atualizar_lista_turmas()
        except Exception as ex:
            mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

    def on_salvar_evento(e):
        titulo = (tf_ev_titulo.value or "").strip()
        if not titulo:
            mostrar_msg("Informe o titulo do evento.", ft.Colors.RED_400)
            return
        tipo = dd_ev_tipo.value or "recesso"
        try:
            criar_evento(
                titulo=titulo,
                data=tf_ev_data.value.strip(),
                tipo=tipo,
            )
            tf_ev_titulo.value = ""
            tf_ev_titulo.update()
            mostrar_msg(f"Evento '{titulo}' cadastrado.")
            atualizar_lista_eventos()

            if tipo in ("feriado", "recesso"):
                n = regenerar_todas_turmas_ativas()
                mostrar_msg(
                    f"Evento salvo. {n} novas aulas geradas (feriados/recessos respeitados)."
                )
                atualizar_lista_turmas()
                if turma_selecionada_id["id"]:
                    carregar_aulas_turma(turma_selecionada_id["id"])
        except Exception as ex:
            mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

    def on_excluir_evento(e):
        excluir_evento(e.control.data)
        mostrar_msg("Evento removido.", ft.Colors.ORANGE_400)
        atualizar_lista_eventos()

    def on_backup(e):
        try:
            caminho = fazer_backup()
            mostrar_msg(f"Backup salvo em: {caminho}")
        except Exception as ex:
            mostrar_msg(f"Erro no backup: {ex}", ft.Colors.RED_400)

    # ---------- layout ----------
    form_turma = ft.Container(
        content=ft.Column(
            [
                ft.Text("Nova turma", size=16, weight=ft.FontWeight.W_600),
                tf_nome,
                tf_disciplina,
                ft.Text("Dias:", size=12),
                ft.Row(list(dias_checks.values()), wrap=True, spacing=4),
                ft.Row([tf_inicio, tf_fim], spacing=8),
                ft.ElevatedButton(
                    "Salvar turma + gerar aulas",
                    icon=ft.Icons.SAVE,
                    on_click=on_salvar_turma,
                ),
            ],
            spacing=8,
        ),
        padding=12,
        border=ft.Border.all(1, ft.Colors.GREY_800),
        border_radius=10,
        width=300,
    )

    form_evento = ft.Container(
        content=ft.Column(
            [
                ft.Text("Novo evento", size=16, weight=ft.FontWeight.W_600),
                tf_ev_titulo,
                ft.Row([tf_ev_data, dd_ev_tipo], spacing=8),
                ft.ElevatedButton(
                    "Salvar evento",
                    icon=ft.Icons.EVENT,
                    on_click=on_salvar_evento,
                ),
                ft.Text("Eventos cadastrados", size=13, weight=ft.FontWeight.W_500),
                lista_eventos_col,
            ],
            spacing=8,
        ),
        padding=12,
        border=ft.Border.all(1, ft.Colors.GREY_800),
        border_radius=10,
        width=300,
    )

    form_backup = ft.Container(
        content=ft.Column(
            [
                ft.Text("Backup", size=16, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Copia o banco para data/backups/ com data e hora no nome.",
                    size=11,
                    color=ft.Colors.GREY_500,
                ),
                ft.OutlinedButton(
                    "Fazer backup do banco",
                    icon=ft.Icons.BACKUP,
                    on_click=on_backup,
                ),
            ],
            spacing=8,
        ),
        padding=12,
        border=ft.Border.all(1, ft.Colors.GREY_800),
        border_radius=10,
        width=300,
    )

    coluna_esquerda = ft.Column(
        [form_turma, form_evento, form_backup],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        width=320,
    )

    coluna_centro = ft.Column(
        [
            ft.Text("Turmas", size=16, weight=ft.FontWeight.W_600),
            lista_turmas_col,
        ],
        expand=True,
        spacing=8,
    )

    coluna_direita = ft.Column(
        [
            ft.Text("Aulas da turma selecionada", size=16, weight=ft.FontWeight.W_600),
            ft.Text(
                "Altere a data e clique em salvar para remarcar.",
                size=11,
                color=ft.Colors.GREY_500,
            ),
            painel_aulas,
        ],
        expand=True,
        spacing=8,
        width=340,
    )

    # carga inicial
    turmas = listar_turmas()
    if not turmas:
        lista_turmas_col.controls.append(
            ft.Text("Nenhuma turma cadastrada.", italic=True, color=ft.Colors.GREY_500)
        )
    else:
        for t in turmas:
            lista_turmas_col.controls.append(montar_card_turma(t))

    eventos = listar_eventos()
    if not eventos:
        lista_eventos_col.controls.append(
            ft.Text("Nenhum evento.", italic=True, color=ft.Colors.GREY_500, size=12)
        )
    else:
        for ev in eventos:
            cor = ev.get("cor") or "#9C27B0"
            lista_eventos_col.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(width=6, height=28, bgcolor=cor, border_radius=3),
                            ft.Column(
                                [
                                    ft.Text(f"{ev['data']} — {ev['titulo']}", size=12),
                                    ft.Text(ev["tipo"], size=10, color=ft.Colors.GREY_500),
                                ],
                                spacing=0,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=14,
                                icon_color=ft.Colors.RED_300,
                                data=ev["id"],
                                on_click=on_excluir_evento,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=6,
                    border=ft.Border.all(1, ft.Colors.GREY_800),
                    border_radius=6,
                )
            )

    painel_aulas.controls.append(
        ft.Text("Clique numa turma para ver as aulas.", italic=True, color=ft.Colors.GREY_500)
    )

    return ft.Column(
        [
            ft.Text("Gerenciar", size=26, weight=ft.FontWeight.BOLD),
            mensagem,
            ft.Divider(height=1),
            ft.Row(
                [
                    coluna_esquerda,
                    ft.VerticalDivider(width=1),
                    coluna_centro,
                    ft.VerticalDivider(width=1),
                    coluna_direita,
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        expand=True,
        spacing=8,
    )