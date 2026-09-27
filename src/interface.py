"""
DevIssues - src/interface.py
Módulo de Interface com o Utilizador (Pessoa 3)

Interface interativa via terminal com cores ANSI, gráficos em ASCII,
carregamento automático de estado e navegação fluida.
"""

import csv
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from src.analise import executar_analise_completa, calcular_estatisticas
from src.coleta import coletar_issues_de_varios_repositorios, salvar_em_csv

# Cores ANSI para o terminal (compatível com Windows/Linux/Mac)
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"


def limpar_tela() -> None:
    """Limpa o terminal conforme o sistema operacional."""
    os.system("cls" if os.name == "nt" else "clear")


def desenhar_barra(percentual: float, largura: int = 20) -> str:
    """Gera uma barra visual de progresso em ASCII (ex: ████████░░ 80.0%)."""
    preenchido = int((percentual / 100) * largura)
    vazio = largura - preenchido
    return f"[{GREEN}{'█' * preenchido}{RESET}{'░' * vazio}] {percentual:.1f}%"


def exibir_cabecalho() -> None:
    """Exibe um banner visualmente atraente."""
    print(f"{CYAN}{'=' * 68}{RESET}")
    print(f"{BOLD}{MAGENTA}            DEVISSUES — DASHBOARD & ANALYTICS DE SOFTWARE          {RESET}")
    print(f"{BLUE}      Análise de Bugs, Dívida Técnica, Urgência e Sentimentos      {RESET}")
    print(f"{CYAN}{'=' * 68}{RESET}\n")


def carregar_dados_existentes() -> Dict[str, Any]:
    """Carrega automaticamente os resultados do CSV se já existirem no disco."""
    caminho = Path("resultados/relatorio_final.csv")
    if not caminho.exists():
        return {}

    issues = []
    try:
        with open(caminho, mode="r", encoding="utf-8-sig") as arq:
            leitor = csv.DictReader(arq)
            issues = list(leitor)
        return calcular_estatisticas(issues)
    except Exception:
        return {}


def menu_coleta() -> None:
    """Submenu interativo para recolha de dados."""
    limpar_tela()
    exibir_cabecalho()
    print(f"{BOLD}[ 1. RECOLHA DE ISSUES VIA GITHUB API ]{RESET}\n")

    print(f"{YELLOW}Opções rápidas de repositórios:{RESET}")
    print(" 1 - Predefinição Python (pallets/flask, psf/requests, fastapi/fastapi)")
    print(" 2 - Inserir repositórios manualmente")
    print(" 0 - Voltar")

    choice = input(f"\n{BOLD}Escolha uma opção:> {RESET}").strip()

    if choice == "1":
        lista_repos = ["pallets/flask", "psf/requests", "fastapi/fastapi"]
    elif choice == "2":
        repos_input = input(
            f"\n{BOLD}Digite os repositórios (ex: owner/repo1, owner/repo2):> {RESET}"
        ).strip()
        if not repos_input:
            print(f"{RED}[!] Nenhum repositório informado.{RESET}")
            return
        lista_repos = [r.strip() for r in repos_input.split(",") if r.strip()]
    else:
        return

    limite_input = input(
        f"{BOLD}Quantidade de issues por repositório (Padrão: 50):> {RESET}"
    ).strip()
    max_issues = int(limite_input) if limite_input.isdigit() else 50

    print(f"\n{CYAN}[*] A recolher dados do GitHub...{RESET}")
    try:
        issues = coletar_issues_de_varios_repositorios(lista_repos, max_por_repo=max_issues)
        salvar_em_csv(issues, "dados/issues.csv")
        print(f"\n{GREEN}[✓] Recolha concluída com sucesso! Dados salvos em 'dados/issues.csv'.{RESET}")
    except Exception as e:
        print(f"\n{RED}[!] Erro na recolha: {e}{RESET}")


def exibir_dashboard(dados: Dict[str, Any]) -> None:
    """Exibe o dashboard estatístico com gráficos ASCII e cores."""
    if not dados or dados.get("total_issues", 0) == 0:
        print(f"{YELLOW}[!] Nenhum dado processado em memória.{RESET}")
        print("Execute primeiro o processamento na opção 2 ou faça a recolha na opção 1.")
        return

    total = dados["total_issues"]
    print(f"{BOLD}{CYAN}=== DASHBOARD DE ANÁLISE LINGUÍSTICA (Total: {total} Issues) ==={RESET}\n")

    # Categorias com barras de progresso
    print(f"{BOLD}CATEGORIAS DETETADAS:{RESET}")
    for cat_key, nome, cor in [
        ("bug", "Bugs / Erros", RED),
        ("divida_tecnica", "Dívida Técnica", YELLOW),
        ("feature_request", "Feature Requests", BLUE),
        ("urgencia", "Casos Urgentes", MAGENTA),
    ]:
        qtd = dados.get(cat_key, 0)
        perc = (qtd / total) * 100
        barra = desenhar_barra(perc)
        print(f" • {cor}{nome:<18}{RESET} | {qtd:>3} issues | {barra}")

    # Sentimento
    print(f"\n{BOLD}DISTRIBUIÇÃO DE SENTIMENTO (SPAÇY LEMMAS):{RESET}")
    sent = dados.get("sentimento", {})
    for s_nome, cor in [("Positivo", GREEN), ("Neutro", YELLOW), ("Negativo", RED)]:
        qtd = sent.get(s_nome, 0)
        perc = (qtd / total) * 100 if total > 0 else 0
        barra = desenhar_barra(perc)
        print(f" • {cor}{s_nome:<18}{RESET} | {qtd:>3} issues | {barra}")

    # Top Erros e Versões
    if dados.get("top_erros"):
        print(f"\n{BOLD}TOP EXCEÇÕES / ERROS (REGEX):{RESET}")
        for erro, qtd in dados["top_erros"]:
            print(f"   - {RED}{erro}{RESET}: {qtd} ocorrência(s)")

    if dados.get("top_versoes"):
        print(f"\n{BOLD}TOP VERSÕES MENCIONADAS (REGEX):{RESET}")
        for ver, qtd in dados["top_versoes"]:
            print(f"   - {CYAN}{ver}{RESET}: {qtd} ocorrência(s)")


def explorar_categoria(dados: Dict[str, Any]) -> None:
    """Submenu para explorar issues detalhadas por categoria."""
    if not dados or "issues_detalhadas" not in dados:
        print(f"{YELLOW}[!] Não há dados detalhados para explorar.{RESET}")
        return

    limpar_tela()
    exibir_cabecalho()
    print(f"{BOLD}[ FILTRAR E EXPLORAR ISSUES ]{RESET}\n")
    print(" 1 - Ver apenas Bugs / Erros")
    print(" 2 - Ver apenas Dívida Técnica")
    print(" 3 - Ver apenas Relatos Urgentes")
    print(" 4 - Ver apenas Feature Requests")
    print(" 0 - Voltar")

    op = input(f"\n{BOLD}Escolha uma opção:> {RESET}").strip()
    mapa = {
        "1": ("bug", "Bugs / Erros", RED),
        "2": ("divida_tecnica", "Dívida Técnica", YELLOW),
        "3": ("urgencia", "Relatos Urgentes", MAGENTA),
        "4": ("feature_request", "Feature Requests", BLUE),
    }

    if op not in mapa:
        return

    chave, titulo, cor = mapa[op]
    issues = [i for i in dados["issues_detalhadas"] if i.get(chave) == "SIM"]

    limpar_tela()
    exibir_cabecalho()
    print(f"{BOLD}A mostrar resultados para: {cor}{titulo.upper()}{RESET} (Total: {len(issues)})\n")

    if not issues:
        print("Nenhuma issue encontrada para esta categoria.")
        return

    for item in issues[:6]:  # Exibe os primeiros 6 para manter o terminal limpo
        print(f"{CYAN}[#{item.get('numero')}] {item.get('titulo')}{RESET}")
        print(f"   Repo: {BOLD}{item.get('repositorio')}{RESET} | Idioma: {item.get('idioma', '').upper()} | Sentimento: {item.get('sentimento')}")
        if item.get("erros_encontrados"):
            print(f"   Erros: {RED}{item.get('erros_encontrados')}{RESET}")
        print("-" * 65)

    if len(issues) > 6:
        print(f"\n{YELLOW}... e mais {len(issues) - 6} issues guardadas em 'resultados/relatorio_final.csv'.{RESET}")


def executar_menu() -> None:
    """Loop principal da aplicação com gestão automática de estado."""
    # Tenta carregar automaticamente se o ficheiro consolidado já existir
    dados_processados = carregar_dados_existentes()

    while True:
        limpar_tela()
        exibir_cabecalho()

        # Indicador de Estado no topo do menu
        if dados_processados and dados_processados.get("total_issues", 0) > 0:
            print(f"{GREEN}[●] Estado: Base carregada com {dados_processados['total_issues']} issues.{RESET}\n")
        else:
            print(f"{YELLOW}[○] Estado: Nenhum resultado carregado em memória.{RESET}\n")

        print(f"{BOLD}MENU PRINCIPAL:{RESET}")
        print(f" {CYAN}1{RESET} - Dashboard & Estatísticas Visuais (Gráficos ASCII)")
        print(f" {CYAN}2{RESET} - Explorar e Filtrar Issues por Categoria")
        print(f" {CYAN}3{RESET} - Executar Pipeline de Análise (Regex + spaCy + Sentimento)")
        print(f" {CYAN}4{RESET} - Recolher Novas Issues (GitHub API)")
        print(f" {CYAN}0{RESET} - Sair")

        opcao = input(f"\n{BOLD}Escolha uma opção (0-4):> {RESET}").strip()

        if opcao == "1":
            limpar_tela()
            exibir_cabecalho()
            exibir_dashboard(dados_processados)
            input(f"\n{BOLD}Pressione ENTER para voltar ao menu...{RESET}")
        elif opcao == "2":
            explorar_categoria(dados_processados)
            input(f"\n{BOLD}Pressione ENTER para voltar ao menu...{RESET}")
        elif opcao == "3":
            limpar_tela()
            exibir_cabecalho()
            dados_processados = executar_analise_completa()
            input(f"\n{BOLD}Pressione ENTER para voltar ao menu...{RESET}")
        elif opcao == "4":
            menu_coleta()
            input(f"\n{BOLD}Pressione ENTER para voltar ao menu...{RESET}")
        elif opcao == "0":
            print(f"\n{GREEN}A encerrar o DevIssues... Bom trabalho na apresentação!{RESET}")
            sys.exit(0)
        else:
            print(f"\n{RED}Opção inválida!{RESET}")
            input("Pressione ENTER para tentar novamente...")


if __name__ == "__main__":
    executar_menu()