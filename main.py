"""
DevIssues - main.py

Ponto de entrada do projeto. Por enquanto, só aciona a coleta de issues
(src/coleta.py). Conforme os outros componentes (Regex, spaCy, análise,
interface) forem ficando prontos, dá pra chamá-los aqui também.
"""

from src.coleta import coletar_issues_de_varios_repositorios, salvar_em_csv

# ------------------------------------------------------------------
# Repositórios e quantidades definidos pelo grupo.
# Se quiser mudar depois, é só editar aqui.
# ------------------------------------------------------------------
REPOSITORIOS = ["psf/requests", "pandas-dev/pandas", "microsoft/vscode", "filipedeschamps/tabnews.com.br"]
QUANTIDADE_POR_REPO = [70, 70, 70, 70]  # total: 280 issues
ARQUIVO_SAIDA = "dados/issues.csv"


def main() -> None:
    print(f"Coletando issues de {len(REPOSITORIOS)} repositório(s)...")
    issues = coletar_issues_de_varios_repositorios(REPOSITORIOS, QUANTIDADE_POR_REPO)
    salvar_em_csv(issues, ARQUIVO_SAIDA)


if __name__ == "__main__":
    main()