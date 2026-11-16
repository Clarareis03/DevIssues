from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from src.nlp import montar_texto_issue


# =========================================================
# 1. CONFIGURAÇÕES
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = ROOT_DIR / "dados" / "issues.csv"
PASTA_RESULTADOS = ROOT_DIR / "resultados"

ARQUIVO_EMBEDDINGS = PASTA_RESULTADOS / "embeddings.npy"
ARQUIVO_RESULTADOS = PASTA_RESULTADOS / "embeddings_resultados.csv"
ARQUIVO_GRAFICO = PASTA_RESULTADOS / "clusters_pca.png"

# Modelo multilíngue para português e inglês
NOME_MODELO = "paraphrase-multilingual-MiniLM-L12-v2"

# Quantidade inicial de grupos
NUM_CLUSTERS = 4

# Quantidade de issues que serão exibidas na busca
TOP_K = 5


# =========================================================
# 2. CARREGAMENTO DOS DADOS
# =========================================================

def carregar_issues():
    """
    Carrega as issues do CSV e prepara os textos.

    Retorna um DataFrame com uma coluna chamada texto.
    """

    if not ARQUIVO_ENTRADA.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO_ENTRADA}"
        )

    df = pd.read_csv(ARQUIVO_ENTRADA)

    colunas_obrigatorias = [
        "repositorio",
        "numero",
        "titulo",
        "corpo"
    ]

    for coluna in colunas_obrigatorias:
        if coluna not in df.columns:
            raise ValueError(
                f"Coluna obrigatória não encontrada: {coluna}"
            )

    df = df.copy()

    # Evita problemas com valores ausentes
    df["titulo"] = df["titulo"].fillna("")
    df["corpo"] = df["corpo"].fillna("")

    # Combina título e corpo utilizando função da etapa anterior
    df["texto"] = [
        montar_texto_issue(titulo, corpo)
        for titulo, corpo in zip(df["titulo"], df["corpo"])
    ]

    # Remove issues sem conteúdo textual
    df = df[df["texto"].str.strip() != ""].copy()

    df.reset_index(drop=True, inplace=True)

    print(f"\nTotal de issues carregadas: {len(df)}")

    return df


# =========================================================
# 3. CARREGAMENTO DO MODELO
# =========================================================

def carregar_modelo():
    """
    Carrega o modelo Sentence Transformers.
    """

    print("\nCarregando modelo de embeddings...")

    modelo = SentenceTransformer(NOME_MODELO)

    print("Modelo carregado com sucesso!")

    return modelo


# =========================================================
# 4. GERAÇÃO DOS EMBEDDINGS
# =========================================================

def gerar_embeddings(df, modelo):
    """
    Transforma os textos das issues em vetores numéricos.

    Cada issue recebe um vetor de representação semântica.
    """

    print("\nGerando embeddings...")

    textos = df["texto"].tolist()

    embeddings = modelo.encode(
        textos,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print("\nEmbeddings gerados!")
    print(f"Formato da matriz: {embeddings.shape}")

    return embeddings


# =========================================================
# 5. SALVAMENTO DOS EMBEDDINGS
# =========================================================

def salvar_embeddings(embeddings):
    """
    Salva a matriz de embeddings em formato NPY.
    """

    PASTA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    np.save(ARQUIVO_EMBEDDINGS, embeddings)

    print(f"\nEmbeddings salvos em: {ARQUIVO_EMBEDDINGS}")


# =========================================================
# 6. BUSCA SEMÂNTICA
# =========================================================

def buscar_issues_semelhantes(
    consulta,
    modelo,
    embeddings,
    df,
    top_k=TOP_K
):
    """
    Recebe uma consulta textual e encontra as issues
    semanticamente mais semelhantes.

    A comparação é realizada pela similaridade do cosseno.
    """

    if not consulta.strip():
        raise ValueError("A consulta não pode estar vazia.")

    print(f"\nConsulta: {consulta}")

    # Transforma a consulta em um embedding
    vetor_consulta = modelo.encode(
        [consulta],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Calcula a similaridade com todas as issues
    similaridades = cosine_similarity(
        vetor_consulta,
        embeddings
    )[0]

    # Identifica os índices das maiores similaridades
    indices = np.argsort(similaridades)[::-1][:top_k]

    resultados = df.iloc[indices][
        ["repositorio", "numero", "titulo"]
    ].copy()

    resultados["similaridade"] = similaridades[indices]

    return resultados


# =========================================================
# 7. AGRUPAMENTO COM KMEANS
# =========================================================

def agrupar_issues(embeddings, num_clusters=NUM_CLUSTERS):
    """
    Agrupa as issues utilizando o algoritmo KMeans.

    Os vetores já estão normalizados.
    """

    print("\nExecutando agrupamento KMeans...")

    if num_clusters < 2 or num_clusters > len(embeddings):
        raise ValueError("Quantidade de clusters inválida.")

    kmeans = KMeans(
        n_clusters=num_clusters,
        random_state=42,
        n_init=10
    )

    clusters = kmeans.fit_predict(embeddings)

    print("\nAgrupamento concluído!")

    return clusters


# =========================================================
# 8. REDUÇÃO DE DIMENSIONALIDADE COM PCA
# =========================================================

def aplicar_pca(embeddings):
    """
    Reduz os vetores para duas dimensões.

    Isso permite representar graficamente os embeddings.
    """

    print("\nAplicando PCA...")

    pca = PCA(n_components=2)

    coordenadas = pca.fit_transform(embeddings)

    variancia = pca.explained_variance_ratio_.sum() * 100

    print(
        f"Variância explicada pelas duas dimensões: "
        f"{variancia:.2f}%"
    )

    return coordenadas, pca


# =========================================================
# 9. VISUALIZAÇÃO DOS CLUSTERS
# =========================================================

def gerar_grafico(df, coordenadas):
    """
    Gera um gráfico de dispersão dos clusters.
    """

    print("\nGerando gráfico dos agrupamentos...")

    plt.figure(figsize=(12, 8))

    for cluster in sorted(df["cluster"].unique()):

        grupo = df[df["cluster"] == cluster]

        plt.scatter(
            grupo["pca_1"],
            grupo["pca_2"],
            label=f"Cluster {cluster}",
            alpha=0.7
        )

    plt.title(
        "DevIssues - Agrupamento Semântico das Issues"
    )

    plt.xlabel("Componente Principal 1")
    plt.ylabel("Componente Principal 2")

    plt.legend()
    plt.grid(alpha=0.2)

    plt.tight_layout()

    plt.savefig(
        ARQUIVO_GRAFICO,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Gráfico salvo em: {ARQUIVO_GRAFICO}")


# =========================================================
# 10. SALVAMENTO DOS RESULTADOS
# =========================================================

def salvar_resultados(df):
    """
    Exporta as informações dos agrupamentos e coordenadas.
    """

    df.to_csv(
        ARQUIVO_RESULTADOS,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\nResultados salvos em: {ARQUIVO_RESULTADOS}"
    )


# =========================================================
# 11. RESUMO DOS AGRUPAMENTOS
# =========================================================

def imprimir_resumo(df):
    """
    Exibe a quantidade de issues em cada cluster.
    """

    print("\n" + "=" * 55)
    print("DEVISSUES - RESUMO DOS AGRUPAMENTOS")
    print("=" * 55)

    print(f"\nTotal de issues: {len(df)}")

    distribuicao = df["cluster"].value_counts().sort_index()

    for cluster, quantidade in distribuicao.items():

        percentual = (quantidade / len(df)) * 100

        print(
            f"Cluster {cluster}: "
            f"{quantidade} issues ({percentual:.1f}%)"
        )

    print("\n" + "=" * 55)


# =========================================================
# 12. EXECUÇÃO PRINCIPAL
# =========================================================

def main():

    print("\n" + "=" * 55)
    print("DEVISSUES - TRILHA B: EMBEDDINGS")
    print("=" * 55)

    # Carregar dados
    df = carregar_issues()

    # Carregar modelo
    modelo = carregar_modelo()

    # Gerar embeddings
    embeddings = gerar_embeddings(df, modelo)

    # Salvar matriz
    salvar_embeddings(embeddings)

    # Agrupar issues
    df["cluster"] = agrupar_issues(embeddings)

    # Aplicar PCA
    coordenadas, pca = aplicar_pca(embeddings)

    df["pca_1"] = coordenadas[:, 0]
    df["pca_2"] = coordenadas[:, 1]

    # Gerar gráfico
    gerar_grafico(df, coordenadas)

    # Salvar resultados
    salvar_resultados(df)

    # Exibir resumo
    imprimir_resumo(df)

    # Exemplo de busca semântica
    print("\n" + "=" * 55)
    print("EXEMPLO DE BUSCA SEMÂNTICA")
    print("=" * 55)

    consulta = "Error when connecting to database"

    resultados_busca = buscar_issues_semelhantes(
        consulta,
        modelo,
        embeddings,
        df,
        top_k=TOP_K
    )

    print(resultados_busca.to_string(index=False))

    print("\nPipeline de embeddings finalizado!")


if __name__ == "__main__":
    main()