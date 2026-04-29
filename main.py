import flet as ft
import traceback

# --- IMPORTAÇÃO DO SUPABASE ---
try:
    from supabase import create_client, Client
    SUPABASE_INSTALADO = True
except ImportError:
    SUPABASE_INSTALADO = False

# As chaves do nosso cofre da Sericom!
URL_SUPABASE = "https://rjcgswtifmdabqsfwifg.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqY2dzd3RpZm1kYWJxc2Z3aWZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0MjMxOTQsImV4cCI6MjA5MDk5OTE5NH0.7qtIV7a44s-38SrZ_ODYepiy-UugcZPA0Yp006jmVs0"

if SUPABASE_INSTALADO:
    supabase: Client = create_client(URL_SUPABASE, CHAVE_SUPABASE)

def main(page: ft.Page):
    # --- CONFIGURAÇÕES DO APP ---
    page.title = "Sericom Turmas"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.scroll = "hidden" # O scroll vai ficar na lista de turmas

    # --- CABEÇALHO DE RESPEITO ---
    cabecalho = ft.Container(
        padding=ft.padding.only(top=40, bottom=20, left=20, right=20),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.Colors.RED_900, ft.Colors.BLACK]
        ),
        border=ft.border.only(bottom=ft.border.BorderSide(2, ft.Colors.RED_600)),
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SCHOOL, color=ft.Colors.WHITE, size=30),
                ft.Text("SERICOM TURMAS", size=24, weight="bold", color=ft.Colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("Professor Apolinário", size=16, color=ft.Colors.GREY_400, italic=True, text_align=ft.TextAlign.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # --- ÁREA ONDE AS TURMAS VÃO APARECER ---
    lista_turmas_ui = ft.ListView(expand=True, padding=15, spacing=15)

    # --- FUNÇÃO MESTRA: BUSCAR E ORGANIZAR DADOS ---
    def carregar_dados(e=None):
        lista_turmas_ui.controls.clear()
        lista_turmas_ui.controls.append(
            ft.Column([
                ft.ProgressRing(color=ft.Colors.RED_600),
                ft.Text("Buscando dados no servidor...", color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

        try:
            # Puxa todo mundo da tabela arena_usuarios
            resposta = supabase.table("arena_usuarios").select("nome_aluno, turma").execute()
            dados_alunos = resposta.data if resposta.data else []

            # Organiza os alunos dentro de suas respectivas turmas (Dicionário)
            turmas_agrupadas = {}
            for aluno in dados_alunos:
                nome_turma = aluno.get('turma')
                # Se o campo estiver vazio ou nulo, joga numa lista de "Sem Turma"
                if not nome_turma or nome_turma.strip() == "":
                    nome_turma = "Alunos Sem Turma Definida"
                
                nome_aluno = aluno.get('nome_aluno') or "Aluno sem nome"

                if nome_turma not in turmas_agrupadas:
                    turmas_agrupadas[nome_turma] = []
                
                turmas_agrupadas[nome_turma].append(nome_aluno)

            # Limpa o carregamento
            lista_turmas_ui.controls.clear()

            # Se o banco estiver vazio
            if not turmas_agrupadas:
                lista_turmas_ui.controls.append(
                    ft.Text("Nenhuma turma ou aluno encontrado no sistema.", color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
                )
            else:
                # Monta a tela ordenando as turmas por nome (ordem alfabética)
                for turma, alunos in sorted(turmas_agrupadas.items()):
                    alunos.sort() # Ordena os alunos alfabeticamente dentro da turma
                    
                    # Cria a listinha visual de alunos para essa turma
                    visual_alunos = []
                    for idx, nome in enumerate(alunos):
                        visual_alunos.append(
                            ft.Container(
                                padding=10,
                                bgcolor=ft.Colors.GREY_900 if idx % 2 == 0 else ft.Colors.BLACK,
                                border_radius=5,
                                content=ft.Row([
                                    ft.Icon(ft.Icons.PERSON_OUTLINE, color=ft.Colors.RED_400, size=18),
                                    ft.Text(nome, color=ft.Colors.WHITE, size=15)
                                ])
                            )
                        )

                    # Cria a "Sanfona" (ExpansionTile) que abre e fecha
                    cartao_turma = ft.Card(
                        color=ft.Colors.BLACK87,
                        elevation=8,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        content=ft.Container(
                            border=ft.border.all(1, ft.Colors.RED_800),
                            border_radius=10,
                            content=ft.ExpansionTile(
                                title=ft.Text(f"{turma}", weight="bold", color=ft.Colors.WHITE, size=18),
                                subtitle=ft.Text(f"{len(alunos)} aluno(s)", color=ft.Colors.RED_400, size=12),
                                icon_color=ft.Colors.RED_500,
                                collapsed_icon_color=ft.Colors.WHITE,
                                controls_padding=10,
                                controls=[
                                    ft.Column(visual_alunos, spacing=2)
                                ]
                            )
                        )
                    )
                    lista_turmas_ui.controls.append(cartao_turma)

        except Exception as erro:
            lista_turmas_ui.controls.clear()
            lista_turmas_ui.controls.append(
                ft.Container(
                    padding=20,
                    bgcolor=ft.Colors.RED_900,
                    border_radius=10,
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.WHITE, size=40),
                        ft.Text("Erro de Conexão!", weight="bold", color=ft.Colors.WHITE, size=18),
                        ft.Text(str(erro), color=ft.Colors.WHITE)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            )

        page.update()

    # --- BOTÃO FLUTUANTE DE ATUALIZAR ---
    botao_atualizar = ft.FloatingActionButton(
        icon=ft.Icons.REFRESH,
        bgcolor=ft.Colors.RED_700,
        shape=ft.CircleBorder(),
        on_click=carregar_dados
    )
    page.floating_action_button = botao_atualizar

    # --- MONTAGEM DA TELA PRINCIPAL ---
    page.add(
        ft.Column([
            cabecalho,
            ft.Container(
                expand=True,
                content=lista_turmas_ui
            )
        ], expand=True, spacing=0)
    )

    # Dispara a primeira busca de dados assim que o app abre
    carregar_dados()

ft.app(target=main)
