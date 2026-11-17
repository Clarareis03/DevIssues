
from pathlib import Path
import pandas as pd

# Caminho principal do projeto
ROOT = Path(__file__).resolve().parent.parent
RESULTADOS = ROOT / "resultados"

ARQUIVOS = {
    "spacy": "spacy_avancado.csv",
    "comparacao_regex": "spacy_vs_regex.csv",
    "embeddings": "embeddings_resultados.csv",
    "transformers": "transformers_resultados.csv",
    "comparacao_transformers": "transformers_vs_etapa1.csv",
    "avaliacao": "avaliacao_transformers.csv",
}


def carregar_resultado(nome):
    """Carrega um resultado da segunda etapa."""
    if nome not in ARQUIVOS:
        raise ValueError(f"Resultado desconhecido: {nome}")

    caminho = RESULTADOS / ARQUIVOS[nome]

    if not caminho.exists():
        return None

    return pd.read_csv(caminho, encoding="utf-8-sig")


def verificar_integracao():
    """Confere quais resultados estão disponíveis."""
    print("\n=== DEVISSUES: INTEGRAÇÃO DA 2ª ETAPA ===")

    for nome in ARQUIVOS:
        dados = carregar_resultado(nome)

        if dados is None:
            print(f"[PENDENTE] {ARQUIVOS[nome]}")
        else:
            print(
                f"[OK] {ARQUIVOS[nome]} "
                f"({len(dados)} linhas)"
            )


if __name__ == "__main__":
    verificar_integracao()
