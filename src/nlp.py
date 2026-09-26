import os
import pandas as pd
import spacy


ARQUIVO_ENTRADA = "dados/issues.csv"
ARQUIVO_SAIDA = "resultados/nlp_results.csv"


def carregar_modelos():
    """
    Carrega os modelos spaCy utilizados pelo projeto.

    Retorna:
        dict: modelos disponíveis para inglês e português.
    """

    modelos = {}

    try:
        modelos["en"] = spacy.load("en_core_web_sm")
    except OSError:
        print("Modelo de inglês não encontrado.")

    try:
        modelos["pt"] = spacy.load("pt_core_news_sm")
    except OSError:
        print("Modelo de português não encontrado.")

    return modelos


def texto_seguro(valor):
    """
    Garante que o conteúdo analisado seja uma string.
    """

    if pd.isna(valor):
        return ""

    return str(valor)


def montar_texto_issue(titulo, corpo):
    """
    Combina título e corpo da issue para análise linguística.
    """

    titulo = texto_seguro(titulo)
    corpo = texto_seguro(corpo)

    if titulo and corpo:
        return f"{titulo}. {corpo}"

    return titulo or corpo


def detectar_idioma(texto):
    """
    Faz uma identificação simples do idioma utilizando
    palavras características do português e do inglês.

    O projeto trabalha principalmente com issues em inglês,
    mas mantém suporte ao português.
    """

    texto = texto.lower()

    palavras_portugues = {
        "erro",
        "problema",
        "quando",
        "como",
        "para",
        "não",
        "uma",
        "que",
        "isso",
        "está",
        "está",
        "arquivo",
        "funciona",
        "precisa",
    }

    palavras_ingles = {
        "error",
        "problem",
        "when",
        "how",
        "with",
        "this",
        "that",
        "file",
        "works",
        "need",
        "should",
        "issue",
    }

    palavras = set(texto.split())

    pontos_pt = len(palavras.intersection(palavras_portugues))
    pontos_en = len(palavras.intersection(palavras_ingles))

    if pontos_pt > pontos_en:
        return "pt"

    return "en"


def processar_texto(texto, modelo):
    """
    Processa um texto utilizando spaCy.

    Retorna:
        dict: tokens, lemas, tokens sem stopwords,
              POS e entidades.
    """

    doc = modelo(texto)

    tokens = []
    lemmas = []
    sem_stopwords = []
    pos = []
    entidades = []

    for token in doc:

        if not token.is_space:
            tokens.append(token.text)

            lemmas.append(token.lemma_)

            pos.append({
                "token": token.text,
                "pos": token.pos_
            })

            if not token.is_stop:
                sem_stopwords.append(token.text)

    for entidade in doc.ents:
        entidades.append({
            "texto": entidade.text,
            "tipo": entidade.label_
        })

    return {
        "tokens": tokens,
        "lemmas": lemmas,
        "sem_stopwords": sem_stopwords,
        "pos": pos,
        "entidades": entidades
    }


def tokenizar(texto, modelo):
    """
    Retorna os tokens identificados pelo spaCy.
    """

    doc = modelo(texto)

    return [
        token.text
        for token in doc
        if not token.is_space
    ]


def lematizar(texto, modelo):
    """
    Retorna os lemas dos tokens.
    """

    doc = modelo(texto)

    return [
        token.lemma_
        for token in doc
        if not token.is_space
    ]


def remover_stopwords(texto, modelo):
    """
    Remove stopwords utilizando a lista do spaCy.
    """

    doc = modelo(texto)

    return [
        token.text
        for token in doc
        if not token.is_space and not token.is_stop
    ]


def identificar_pos(texto, modelo):
    """
    Identifica a classe gramatical dos tokens.
    """

    doc = modelo(texto)

    return [
        {
            "token": token.text,
            "pos": token.pos_
        }
        for token in doc
        if not token.is_space
    ]


def extrair_entidades(texto, modelo):
    """
    Extrai entidades nomeadas identificadas pelo spaCy.
    """

    doc = modelo(texto)

    return [
        {
            "texto": entidade.text,
            "tipo": entidade.label_
        }
        for entidade in doc.ents
    ]


def analisar_texto(texto, modelos):
    """
    Detecta o idioma e executa a análise linguística
    utilizando o modelo spaCy correspondente.
    """

    idioma = detectar_idioma(texto)

    modelo = modelos.get(idioma)

    if modelo is None:
        return {
            "idioma": idioma,
            "tokens": [],
            "lemmas": [],
            "sem_stopwords": [],
            "pos": [],
            "entidades": []
        }

    resultado = processar_texto(texto, modelo)

    resultado["idioma"] = idioma

    return resultado


def carregar_issues():
    """
    Carrega as issues coletadas pela etapa de coleta.
    """

    if not os.path.exists(ARQUIVO_ENTRADA):
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

    return df


def processar_issues(df, modelos):
    """
    Processa todas as issues utilizando spaCy.
    """

    resultados = []

    for _, issue in df.iterrows():

        texto = montar_texto_issue(
            issue["titulo"],
            issue["corpo"]
        )

        analise = analisar_texto(
            texto,
            modelos
        )

        resultados.append({
            "repositorio": issue["repositorio"],
            "numero": issue["numero"],
            "titulo": issue["titulo"],
            "idioma": analise["idioma"],
            "tokens": analise["tokens"],
            "lemmas": analise["lemmas"],
            "sem_stopwords": analise["sem_stopwords"],
            "pos": analise["pos"],
            "entidades": analise["entidades"]
        })

    return pd.DataFrame(resultados)


def salvar_resultados(df):
    """
    Salva os resultados da análise linguística.
    """

    os.makedirs(
        os.path.dirname(ARQUIVO_SAIDA),
        exist_ok=True
    )

    df.to_csv(
        ARQUIVO_SAIDA,
        index=False
    )

    print(
        f"\nResultados salvos em: {ARQUIVO_SAIDA}"
    )


def imprimir_resumo(df):
    """
    Exibe um resumo da análise realizada.
    """

    print("\n" + "=" * 55)
    print("DEVISSUES - ANÁLISE NLP COM SPACY")
    print("=" * 55)

    print(
        f"Total de issues analisadas: {len(df)}"
    )

    if "idioma" in df.columns:
        idiomas = df["idioma"].value_counts()

        print("\nIdiomas identificados:")

        for idioma, quantidade in idiomas.items():
            print(
                f"- {idioma}: {quantidade} issues"
            )

    total_tokens = sum(
        len(tokens)
        for tokens in df["tokens"]
    )

    total_entidades = sum(
        len(entidades)
        for entidades in df["entidades"]
    )

    print(
        f"\nTotal de tokens: {total_tokens}"
    )

    print(
        f"Total de entidades: {total_entidades}"
    )

    print("=" * 55)


def main():
    """
    Executa o pipeline completo de análise NLP.
    """

    print("\nCarregando modelos spaCy...")

    modelos = carregar_modelos()

    if not modelos:
        raise RuntimeError(
            "Nenhum modelo spaCy foi carregado."
        )

    print(
        f"Modelos carregados: {', '.join(modelos.keys())}"
    )

    print("\nCarregando issues...")

    df = carregar_issues()

    print(
        f"Issues carregadas: {len(df)}"
    )

    print("\nProcessando textos...")

    resultados = processar_issues(
        df,
        modelos
    )

    salvar_resultados(resultados)

    imprimir_resumo(resultados)


if __name__ == "__main__":
    main()