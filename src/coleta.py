"""
DevIssues - src/coleta.py
Componente de Coleta (Pessoa 1)

Busca issues públicas de repositórios do GitHub usando a API REST oficial
e salva os resultados em dados/issues.csv, que os componentes de Regex
(src/regex.py) e spaCy (src/nlp.py) usam na sequência do pipeline.

------------------------------------------------------------------
COMO CONFIGURAR O TOKEN (uma vez só, na sua máquina)
------------------------------------------------------------------
1. Crie um Personal Access Token fine-grained em
   https://github.com/settings/personal-access-tokens/new
   - Repository access: "Public Repositories (read-only)"
   - Permissions: pode deixar em branco (leitura pública já é automática)
2. Na raiz do projeto (mesma pasta do main.py), crie um arquivo chamado
   ".env" (NÃO commitar) com uma linha:
       GITHUB_TOKEN=cole_seu_token_aqui
3. Instale as dependências: pip install -r requirements.txt

------------------------------------------------------------------
COMO RODAR
------------------------------------------------------------------
Direto pelo terminal, a partir da raiz do projeto:
    python -m src.coleta --repos psf/requests,pallets/flask --max-por-repo 200

Ou importando de outro módulo (ex.: main.py):
    from src.coleta import coletar_issues_de_varios_repositorios, salvar_em_csv
"""

import argparse
import csv
import os
import time
from typing import Any

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()  
except ImportError:
    pass  

GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def verificar_token() -> None:
    """Avisa no console se o token não foi configurado, sem travar o
    programa (a API ainda funciona, só que com limite bem menor)."""
    if not GITHUB_TOKEN:
        print(
            "[AVISO] GITHUB_TOKEN não encontrado (crie um arquivo .env na raiz "
            "do projeto). A coleta seguirá com limite de só 60 requisições/hora.\n"
        )


def buscar_pagina_de_issues(
    owner: str, repo: str, pagina: int, por_pagina: int = 100
) -> list[dict[str, Any]]:
    """Busca uma página de issues (mescladas com PRs, que filtramos depois)
    de um repositório específico."""
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues"
    parametros = {
        "state": "all",
        "per_page": por_pagina,
        "page": pagina,
        "sort": "created",
        "direction": "desc",
    }

    resposta = requests.get(url, headers=HEADERS, params=parametros, timeout=15)

    if resposta.status_code == 403 and "rate limit" in resposta.text.lower():
        reset_em = int(resposta.headers.get("X-RateLimit-Reset", time.time() + 60))
        espera = max(reset_em - time.time(), 5)
        print(f"[RATE LIMIT] Aguardando {int(espera)}s até o limite renovar...")
        time.sleep(espera)
        return buscar_pagina_de_issues(owner, repo, pagina, por_pagina)

    resposta.raise_for_status()
    return resposta.json()


def eh_issue_de_verdade(item: dict[str, Any]) -> bool:
    """A API /issues do GitHub devolve issues E pull requests juntos.
    Descartamos quem tem a chave 'pull_request'."""
    return "pull_request" not in item


def extrair_campos_relevantes(item: dict[str, Any], repo_nome: str) -> dict[str, Any]:
    """Reduz o JSON da issue aos campos usados pelo restante do pipeline
    (Regex em src/regex.py e spaCy em src/nlp.py)."""
    return {
        "repositorio": repo_nome,
        "numero": item["number"],
        "titulo": item["title"],
        "corpo": (item.get("body") or "").replace("\n", " ").strip(),
        "estado": item["state"],
        "criado_em": item["created_at"],
        "fechado_em": item.get("closed_at") or "",
        "comentarios": item["comments"],
        "labels": ";".join(label["name"] for label in item.get("labels", [])),
        "url": item["html_url"],
    }


def coletar_issues_de_um_repositorio(
    owner: str, repo: str, max_issues: int = 200
) -> list[dict[str, Any]]:
    """Pagina pela API até juntar max_issues issues (descontando PRs) ou até
    o repositório acabar as páginas."""
    issues_coletadas: list[dict[str, Any]] = []
    pagina = 1

    while len(issues_coletadas) < max_issues:
        itens = buscar_pagina_de_issues(owner, repo, pagina)
        if not itens:
            break

        for item in itens:
            if eh_issue_de_verdade(item):
                issues_coletadas.append(extrair_campos_relevantes(item, f"{owner}/{repo}"))
            if len(issues_coletadas) >= max_issues:
                break

        pagina += 1

    print(f"  -> {owner}/{repo}: {len(issues_coletadas)} issues coletadas")
    return issues_coletadas


def coletar_issues_de_varios_repositorios(
    repositorios: list[str], max_por_repo: int | list[int] = 200
) -> list[dict[str, Any]]:
    """Recebe uma lista no formato ['owner/repo', ...] e junta as issues
    de todos eles em uma única lista. É esta função que main.py (ou o
    componente de análise) deve importar para acionar a coleta.

    max_por_repo pode ser um único número (mesmo limite para todos) ou uma
    lista com um valor para cada repositório, na mesma ordem, para quando
    o grupo quiser uma quantidade diferente por repositório (ex.: [83, 83, 84])."""
    if isinstance(max_por_repo, int):
        limites = [max_por_repo] * len(repositorios)
    else:
        if len(max_por_repo) != len(repositorios):
            raise ValueError(
                "A quantidade de limites informados não bate com a quantidade de repositórios."
            )
        limites = max_por_repo

    todas_as_issues: list[dict[str, Any]] = []
    for repositorio, limite in zip(repositorios, limites):
        owner, repo = repositorio.strip().split("/")
        todas_as_issues.extend(
            coletar_issues_de_um_repositorio(owner, repo, limite)
        )
    return todas_as_issues


def salvar_em_csv(issues: list[dict[str, Any]], caminho_saida: str = "dados/issues.csv") -> None:
    """Grava a lista de issues em dados/issues.csv, pronto para os
    componentes de Regex e spaCy lerem na sequência do pipeline."""
    if not issues:
        print("[AVISO] Nenhuma issue para salvar.")
        return

    os.makedirs(os.path.dirname(caminho_saida) or ".", exist_ok=True)
    campos = list(issues[0].keys())
    with open(caminho_saida, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(issues)

    print(f"[OK] {len(issues)} issues salvas em {caminho_saida}")


def main() -> None:
    verificar_token()

    parser = argparse.ArgumentParser(description="Coleta de issues do GitHub - DevIssues")
    parser.add_argument(
        "--repos",
        required=True,
        help="Repositórios separados por vírgula, ex: psf/requests,pallets/flask",
    )
    parser.add_argument(
        "--max-por-repo",
        default="200",
        help=(
            "Máximo de issues por repositório. Um único número aplica o mesmo "
            "limite a todos (ex.: 200), ou uma lista separada por vírgula com "
            "um valor por repositório, na mesma ordem de --repos (ex.: 83,83,84)."
        ),
    )
    parser.add_argument(
        "--saida", default="dados/issues.csv", help="Caminho do CSV de saída"
    )
    argumentos = parser.parse_args()

    lista_repos = argumentos.repos.split(",")

    valores_limite = argumentos.max_por_repo.split(",")
    if len(valores_limite) == 1:
        limites: int | list[int] = int(valores_limite[0])
    else:
        limites = [int(valor) for valor in valores_limite]

    print(f"Coletando issues de {len(lista_repos)} repositório(s)...")

    issues = coletar_issues_de_varios_repositorios(lista_repos, limites)
    salvar_em_csv(issues, argumentos.saida)


if __name__ == "__main__":
    main()