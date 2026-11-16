"""
DevIssues - src/pipeline_spacy.py
Trilha A (2ª etapa): pipeline spaCy avançado.

O que este módulo faz:
1. separa as issues por idioma (en / pt) e usa um modelo md para cada um;
2. monta o pipeline: ... -> entity_ruler -> ner -> filtrar_versoes -> resumo_sinais;
3. extrai ERRO, VERSAO, BIBLIOTECA e TECNOLOGIA de cada issue;
4. acha as issues mais parecidas (similaridade do cosseno), sempre dentro do mesmo idioma;
5. compara erros e versões com o Regex da etapa 1.

Rodar a partir da raiz do projeto:
    python -m src.pipeline_spacy
"""

import os
import re

import numpy as np
import pandas as pd
import spacy
from spacy.language import Language
from spacy.tokens import Doc
from spacy.util import compile_infix_regex

from src.nlp import detectar_idioma, montar_texto_issue

ARQUIVO_ENTRADA = "dados/issues.csv"
ARQUIVO_REGEX = "resultados/regex_results.csv"
ARQUIVO_SAIDA = "resultados/spacy_avancado.csv"
ARQUIVO_COMPARACAO = "resultados/spacy_vs_regex.csv"

MODELOS = {"en": "en_core_web_md", "pt": "pt_core_news_md"}
LIMITE_VETOR = 1500  # a similaridade usa só título + início do corpo
K_VIZINHAS = 3

# Listas montadas a partir do que aparece nas 280 issues coletadas
BIBLIOTECAS = [
    "numpy", "pandas", "requests", "urllib3", "pytest", "matplotlib", "scipy",
    "pyarrow", "sqlalchemy", "openpyxl", "react", "electron", "eslint",
]
TECNOLOGIAS = [
    "python", "javascript", "typescript", "node", "nodejs", "docker",
    "postgresql", "postgres", "linux", "windows", "macos", "git", "github",
    "npm", "vercel", "wsl", "ssh", "json", "sql",
]

# Contexto usado para decidir se um número como 3.12 é mesmo uma versão
PISTAS_VERSAO = {"version", "versão", "versao", "release", "build", "rc"} | set(BIBLIOTECAS) | set(TECNOLOGIAS)
UNIDADES_APOS = {"%", "ms", "s", "sec", "seconds", "mb", "gb", "kb", "x", "fps"}
PALAVRAS_ANTES = {"score", "rfc", "section", "line", "lines", "page"}

# Atributos novos no Doc, preenchidos pelo componente customizado
for atributo in ("erros", "versoes", "bibliotecas", "tecnologias"):
    Doc.set_extension(atributo, default=[], force=True)


def parece_versao_real(doc, ent):
    """Usa o contexto ao redor do número para descartar falsos positivos."""
    texto = ent.text
    if ent.end < len(doc) and doc[ent.end].lower_ in UNIDADES_APOS:
        return False
    if ent.start > 0 and doc[ent.start - 1].lower_ in PALAVRAS_ANTES:
        return False
    if texto[0] in "vV" or len(texto.split(".")) >= 3:
        return True  # v2.3.1 ou três partes (3.13.5) já parecem versão
    anteriores = {doc[i].lower_ for i in range(max(0, ent.start - 3), ent.start)}
    return bool(anteriores & PISTAS_VERSAO)  # 3.12 só vale depois de "python", "version"...


@Language.component("filtrar_versoes")
def filtrar_versoes(doc):
    """Componente customizado 1: remove entidades VERSAO que parecem ruído."""
    doc.ents = [e for e in doc.ents if e.label_ != "VERSAO" or parece_versao_real(doc, e)]
    return doc


@Language.component("resumo_sinais")
def resumo_sinais(doc):
    """Componente customizado 2: junta as entidades em atributos doc._."""
    def coletar(rotulo, minusculo=False):
        achados = {e.text.lower() if minusculo else e.text for e in doc.ents if e.label_ == rotulo}
        return sorted(achados)

    doc._.erros = coletar("ERRO")
    doc._.versoes = coletar("VERSAO")
    doc._.bibliotecas = coletar("BIBLIOTECA", minusculo=True)
    doc._.tecnologias = coletar("TECNOLOGIA", minusculo=True)
    return doc


def ajustar_tokenizador(nlp):
    """Faz o tokenizador separar parênteses, aspas, '=', '|', '+' e hífen depois de número.

    Sem isso, em textos de código o nome do erro fica colado na pontuação
    (ex.: 'SSLError(SSLCertVerificationError(1') e o padrão do EntityRuler,
    que olha token por token, não encontra nada.
    """
    infixos = list(nlp.Defaults.infixes) + [
        r"[()\[\]{}\"\\=|+]",  # pontuação e separadores de tabela markdown
        r"(?<=\d)-",  # hífen logo depois de número (2.6.3-py3, 6.8.0-136)
    ]
    nlp.tokenizer.infix_finditer = compile_infix_regex(infixos).finditer


def montar_pipeline(nome_modelo):
    """Carrega o modelo e acrescenta o EntityRuler e os dois componentes nossos."""
    nlp = spacy.load(nome_modelo)
    ajustar_tokenizador(nlp)
    ruler = nlp.add_pipe(
        "entity_ruler",
        before="ner",
        config={"phrase_matcher_attr": "LOWER", "overwrite_ents": True},
    )
    padroes = [
        {"label": "ERRO", "pattern": [{"TEXT": {"REGEX": r"^\w+(Error|Exception)$"}}]},
        {"label": "VERSAO", "pattern": [{"TEXT": {"REGEX": r"^v?\d+\.\d+(\.\d+)?$"}}]},
    ]
    padroes += [{"label": "BIBLIOTECA", "pattern": nome} for nome in BIBLIOTECAS]
    padroes += [{"label": "TECNOLOGIA", "pattern": nome} for nome in TECNOLOGIAS]
    ruler.add_patterns(padroes)

    nlp.add_pipe("filtrar_versoes", after="ner")
    nlp.add_pipe("resumo_sinais", last=True)
    return nlp


def carregar_issues():
    """Lê o CSV da coleta, monta o texto de cada issue e detecta o idioma."""
    df = pd.read_csv(ARQUIVO_ENTRADA)
    df["texto"] = [montar_texto_issue(t, c) for t, c in zip(df["titulo"], df["corpo"])]
    df["idioma"] = df["texto"].apply(detectar_idioma)
    return df


def calcular_vizinhas(nlp, textos, numeros, k=K_VIZINHAS):
    """Para cada issue, devolve as k mais parecidas (cosseno dos vetores médios).

    nlp.make_doc só tokeniza: os vetores vêm direto do vocabulário do modelo md,
    então não é preciso rodar o pipeline inteiro de novo.
    """
    vetores = np.array([nlp.make_doc(t[:LIMITE_VETOR]).vector for t in textos])
    normas = np.linalg.norm(vetores, axis=1, keepdims=True)
    normas[normas == 0] = 1
    unitarios = vetores / normas
    similaridade = unitarios @ unitarios.T  # cos(a, b) = a.b / (|a| |b|)
    np.fill_diagonal(similaridade, -1)

    k = min(k, len(textos) - 1)
    ordem = np.argsort(-similaridade, axis=1)[:, :k]
    return [
        "; ".join(f"{numeros[j]} ({similaridade[i, j]:.2f})" for j in ordem[i])
        for i in range(len(textos))
    ]


def processar_idioma(df, idioma, nome_modelo):
    """Roda o pipeline em todas as issues de um idioma e devolve as colunas novas."""
    grupo = df[df["idioma"] == idioma]
    if grupo.empty:
        return pd.DataFrame()

    nlp = montar_pipeline(nome_modelo)
    print(f"[{idioma}] {len(grupo)} issues | {nome_modelo} | pipeline: {nlp.pipe_names}")

    docs = list(nlp.pipe(grupo["texto"], batch_size=8))
    numeros = grupo["numero"].tolist()
    return pd.DataFrame(
        {
            "erros": ["; ".join(d._.erros) for d in docs],
            "versoes": ["; ".join(d._.versoes) for d in docs],
            "bibliotecas": ["; ".join(d._.bibliotecas) for d in docs],
            "tecnologias": ["; ".join(d._.tecnologias) for d in docs],
            "vizinhas": calcular_vizinhas(nlp, grupo["texto"].tolist(), numeros),
        },
        index=grupo.index,
    )


def numero_da_versao(item):
    """Fica só com a parte numérica do começo: 'v6.8.0-136-generic' vira '6.8.0'.

    O Regex da etapa 1 guarda sufixos como '-generic' e '+deb13'; sem esse ajuste
    o mesmo número apareceria como diferente nos dois métodos.
    """
    achou = re.match(r"v?(\d+(?:\.\d+)+)", item)
    return achou.group(1) if achou else item


def como_conjunto(texto, versao=False):
    """Transforma 'a; b' em {'a', 'b'}, sem diferenciar maiúsculas de minúsculas."""
    itens = {p.strip().lower() for p in str(texto).split(";") if p.strip()}
    return {numero_da_versao(i) for i in itens} if versao else itens


def classificar(achou_spacy, achou_regex):
    """Diz como os dois métodos se comportaram numa mesma issue."""
    if not achou_spacy and not achou_regex:
        return "nenhum"
    if achou_spacy == achou_regex:
        return "igual"
    if not achou_regex:
        return "so_spacy"
    if not achou_spacy:
        return "so_regex"
    return "diferente"


def comparar_com_regex(resultado):
    """Junta o resultado do spaCy com o do Regex (etapa 1) e compara erros e versões."""
    regex = pd.read_csv(ARQUIVO_REGEX).fillna("")
    chave = ["repositorio", "numero"]
    for tabela in (resultado, regex):
        tabela["numero"] = tabela["numero"].astype(str)
    junto = resultado.merge(
        regex[chave + ["erros", "versoes"]], on=chave, suffixes=("_spacy", "_regex")
    )

    for campo, versao in (("erros", False), ("versoes", True)):
        junto[f"status_{campo}"] = [
            classificar(como_conjunto(a, versao), como_conjunto(b, versao))
            for a, b in zip(junto[f"{campo}_spacy"], junto[f"{campo}_regex"])
        ]
    return junto


def imprimir_resumo(comparacao):
    """Mostra no terminal quanto cada método encontrou e onde divergem."""
    for campo in ("erros", "versoes"):
        print(f"\n=== {campo.upper()}: spaCy x Regex ===")
        print(comparacao[f"status_{campo}"].value_counts().to_string())
        divergentes = comparacao[comparacao[f"status_{campo}"].isin(["so_spacy", "so_regex", "diferente"])]
        for _, linha in divergentes.head(5).iterrows():
            print(
                f"  #{linha['numero']} ({linha['repositorio']}) "
                f"spaCy=[{linha[f'{campo}_spacy']}] Regex=[{linha[f'{campo}_regex']}]"
            )


def main():
    df = carregar_issues()
    partes = [processar_idioma(df, idioma, modelo) for idioma, modelo in MODELOS.items()]
    df = df.join(pd.concat(partes))

    os.makedirs(os.path.dirname(ARQUIVO_SAIDA), exist_ok=True)
    colunas = ["repositorio", "numero", "titulo", "idioma", "erros", "versoes",
               "bibliotecas", "tecnologias", "vizinhas"]
    resultado = df[colunas].copy()
    resultado.to_csv(ARQUIVO_SAIDA, index=False)
    print(f"\n[OK] {len(resultado)} issues salvas em {ARQUIVO_SAIDA}")

    comparacao = comparar_com_regex(resultado)
    comparacao.to_csv(ARQUIVO_COMPARACAO, index=False)
    imprimir_resumo(comparacao)
    print(f"\n[OK] comparação salva em {ARQUIVO_COMPARACAO}")


if __name__ == "__main__":
    main()
