import os 

import pandas as pd
import spacy
from spacy.language import Language
from spacy.tokens import Doc

from src.nlp import detectar_idioma, montar_texto_issue


ARQUIVO_ENTRADA = "dados/issues.csv"
ARQUIVO_SAIDA = "resultados/spacy_avancado_prototipo.csv"
QUANTIDADE_PROTOTIPO = 20
LIMITE_CARACTERES = 1500

BIBLIOTECAS = ["numpy", "pandas", "requests", "urllib3", "pytest", "matplotlib", "python"]


# atributos novos no Doc, preenchidos pelo componente customizado
Doc.set_extension("erros", default=[], force=True)
Doc.set_extension("versoes", default=[], force=True)
Doc.set_extension("bibliotecas", default=[], force=True)


@Language.component("resumo_sinais")
def resumo_sinais(doc):
    """Componente customizado: junta as entidades do EntityRuler em doc._."""
    doc._.erros = sorted({e.text for e in doc.ents if e.label_ == "ERRO"})
    doc._.versoes = sorted({e.text for e in doc.ents if e.label_ == "VERSAO"})
    doc._.bibliotecas = sorted({e.text.lower() for e in doc.ents if e.label_ == "BIBLIOTECA"})
    return doc


def montar_pipeline():
    """Carrega o modelo e monta: ... -> entity_ruler -> ner -> resumo_sinais."""
    nlp = spacy.load("en_core_web_md")
 
    ruler = nlp.add_pipe(
        "entity_ruler",
        before="ner",
        config={"phrase_matcher_attr": "LOWER", "overwrite_ents": True},
    )
    padroes = [
        {"label": "ERRO", "pattern": [{"TEXT": {"REGEX": r"^\w*(Error|Exception)$"}}]},
        {"label": "VERSAO", "pattern": [{"TEXT": {"REGEX": r"^v?\d+\.\d+(\.\d+)?$"}}]},
    ]
    padroes += [{"label": "BIBLIOTECA", "pattern": nome} for nome in BIBLIOTECAS]
    ruler.add_patterns(padroes)
 
    nlp.add_pipe("resumo_sinais", last=True)
    return nlp
 
 
def carregar_issues_em_ingles(quantidade):
    """Lê o CSV da coleta e devolve as primeiras issues em inglês."""
    df = pd.read_csv(ARQUIVO_ENTRADA)
    df["texto"] = [
        montar_texto_issue(t, c)[:LIMITE_CARACTERES]
        for t, c in zip(df["titulo"], df["corpo"])
    ]
    df["idioma"] = df["texto"].apply(detectar_idioma)
    ingles = df[df["idioma"] == "en"]
    # pega issues de cada repositório (e não só do primeiro) para a amostra ficar variada
    por_repo = -(-quantidade // ingles["repositorio"].nunique())
    amostra = ingles.groupby("repositorio").head(por_repo).head(quantidade)
    return amostra.reset_index(drop=True)
 
 
def issues_parecidas(docs, indice, k=3):
    """Devolve as k issues mais parecidas com docs[indice] (cosseno dos vetores médios)."""
    notas = [
        (j, docs[indice].similarity(outro))
        for j, outro in enumerate(docs)
        if j != indice
    ]
    return sorted(notas, key=lambda par: par[1], reverse=True)[:k]
 
 
def main():
    nlp = montar_pipeline()
    print("Pipeline:", nlp.pipe_names)
    nlp.analyze_pipes(pretty=True)
 
    df = carregar_issues_em_ingles(QUANTIDADE_PROTOTIPO)
    docs = list(nlp.pipe(df["texto"], batch_size=8))
 
    df["erros"] = [d._.erros for d in docs]
    df["versoes"] = [d._.versoes for d in docs]
    df["bibliotecas"] = [d._.bibliotecas for d in docs]
 
    print(df[["repositorio", "numero", "erros", "versoes", "bibliotecas"]].to_string())
 
    print("\nIssues mais parecidas com a primeira:")
    print("  base:", df.loc[0, "titulo"])
    for j, nota in issues_parecidas(docs, 0):
        print(f"  {nota:.2f} -> {df.loc[j, 'titulo']}")
 
    os.makedirs(os.path.dirname(ARQUIVO_SAIDA), exist_ok=True)
    df.drop(columns=["texto"]).to_csv(ARQUIVO_SAIDA, index=False)
    print(f"\n[OK] protótipo salvo em {ARQUIVO_SAIDA}")
 
 
if __name__ == "__main__":
    main()
