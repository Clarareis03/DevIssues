"""
DevIssues - src/transformers_sent.py
Trilha C (2ª etapa): transformers para sentimento e classificação.

O que este módulo faz:
1. classifica o sentimento de cada issue com um transformer multilíngue
   (negativo / neutro / positivo, com a probabilidade de cada um);
2. classifica o tipo da issue (bug, dívida técnica, feature request) com
   zero-shot, ou seja, sem treinar nada: o modelo decide se cada frase
   "combina" com cada rótulo;
3. compara tudo com a 1ª etapa (léxico + Regex em resultados/relatorio_final.csv);
4. gera uma planilha para rotulagem manual às cegas e calcula acurácia e F1
   dos dois métodos contra esse gabarito.

Rodar a partir da raiz do projeto:
    python -m src.transformers_sent              # roda os modelos e compara com a etapa 1
    python -m src.transformers_sent --amostra    # cria a planilha de rotulagem (60 issues)
    python -m src.transformers_sent --avaliar    # métricas contra os rótulos manuais
"""

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from src.nlp import detectar_idioma, montar_texto_issue


# =========================================================
# 1. CONFIGURAÇÕES
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = ROOT_DIR / "dados" / "issues.csv"
ARQUIVO_ETAPA1 = ROOT_DIR / "resultados" / "relatorio_final.csv"
PASTA_RESULTADOS = ROOT_DIR / "resultados"

ARQUIVO_RESULTADOS = PASTA_RESULTADOS / "transformers_resultados.csv"
ARQUIVO_COMPARACAO = PASTA_RESULTADOS / "transformers_vs_etapa1.csv"
ARQUIVO_GRAFICO = PASTA_RESULTADOS / "sentimento_etapa1_vs_transformer.png"
ARQUIVO_AMOSTRA = PASTA_RESULTADOS / "amostra_rotulagem_sentimento.csv"
ARQUIVO_AVALIACAO = PASTA_RESULTADOS / "avaliacao_transformers.csv"

# Modelo multilíngue (inglês e português) de sentimento, com 3 classes
MODELO_SENTIMENTO = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

# Modelo multilíngue treinado em inferência de linguagem natural (NLI), usado no zero-shot
MODELO_ZERO_SHOT = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"

# Cada rótulo é escrito como frase completa, porque o zero-shot monta
# "This GitHub issue reports {rótulo}." e pergunta se a frase é verdadeira.
ROTULOS_ZERO_SHOT = {
    "bug": "a software bug or an error",
    "divida_tecnica": "technical debt or code that needs refactoring",
    "feature_request": "a feature request or an enhancement",
}
TEMPLATE_ZERO_SHOT = "This GitHub issue reports {}."
LIMIAR_ZERO_SHOT = 0.5

MAX_CARACTERES = 1500   # título + início do corpo; o resto seria cortado pelo modelo mesmo
MAX_TOKENS = 512        # limite de entrada dos dois transformers
TAMANHO_LOTE = 8

CLASSES = ["Negativo", "Neutro", "Positivo"]
INTEGRANTES = ["Ayra", "Ana Beatriz", "Maria Clara"]
ISSUES_POR_REPOSITORIO = 15  # 4 repositórios x 15 = 60 issues (20 por integrante)


# =========================================================
# 2. CARREGAMENTO DOS DADOS
# =========================================================

def carregar_issues():
    """
    Carrega as issues e monta o texto que vai para os modelos.

    Usa montar_texto_issue e detectar_idioma da 1ª etapa, para
    os resultados continuarem comparáveis.
    """

    if not ARQUIVO_ENTRADA.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")

    df = pd.read_csv(ARQUIVO_ENTRADA)
    df["titulo"] = df["titulo"].fillna("")
    df["corpo"] = df["corpo"].fillna("")

    df["texto"] = [
        montar_texto_issue(titulo, corpo)[:MAX_CARACTERES]
        for titulo, corpo in zip(df["titulo"], df["corpo"])
    ]
    df = df[df["texto"].str.strip() != ""].reset_index(drop=True)

    df["idioma"] = [detectar_idioma(texto) for texto in df["texto"]]

    print(f"\nTotal de issues carregadas: {len(df)}")
    return df


# =========================================================
# 3. CARREGAMENTO DOS MODELOS
# =========================================================

def carregar_pipelines(com_tipo=True):
    """
    Carrega os pipelines do Hugging Face.

    Na primeira execução os modelos são baixados (alguns GB no total) e
    ficam no cache do usuário; nas próximas vezes carregam do disco.
    O import fica aqui dentro para o resto do módulo funcionar
    (amostra, avaliação) mesmo sem o transformers instalado.
    """

    from transformers import pipeline

    print(f"\nCarregando modelo de sentimento: {MODELO_SENTIMENTO}")
    pipe_sentimento = pipeline("sentiment-analysis", model=MODELO_SENTIMENTO)

    pipe_zero_shot = None
    if com_tipo:
        print(f"Carregando modelo zero-shot: {MODELO_ZERO_SHOT}")
        pipe_zero_shot = pipeline("zero-shot-classification", model=MODELO_ZERO_SHOT)

    print("Modelos carregados com sucesso!")
    return pipe_sentimento, pipe_zero_shot


# =========================================================
# 4. SENTIMENTO COM TRANSFORMER
# =========================================================

def normalizar_rotulo(rotulo):
    """
    Converte o rótulo do modelo (negative, Neutral, ...) para o
    vocabulário do projeto (Negativo, Neutro, Positivo).
    """

    mapa = {"negative": "Negativo", "neutral": "Neutro", "positive": "Positivo"}
    chave = str(rotulo).strip().lower()

    if chave not in mapa:
        raise ValueError(
            f"Rótulo desconhecido no modelo de sentimento: {rotulo!r}. "
            f"Ajuste normalizar_rotulo() para este modelo."
        )
    return mapa[chave]


def classificar_sentimento(textos, pipe_sentimento):
    """
    Devolve, para cada texto, a classe mais provável e a probabilidade
    das três classes.
    """

    print("\nClassificando sentimento com transformer...")

    saidas = pipe_sentimento(
        textos,
        batch_size=TAMANHO_LOTE,
        truncation=True,
        max_length=MAX_TOKENS,
        top_k=None,  # devolve todas as classes, não só a vencedora
    )

    linhas = []
    for saida in saidas:
        probs = {normalizar_rotulo(item["label"]): item["score"] for item in saida}
        melhor = max(probs, key=probs.get)
        linhas.append({
            "sentimento_transformer": melhor,
            "confianca_sentimento": probs[melhor],
            "p_negativo": probs["Negativo"],
            "p_neutro": probs["Neutro"],
            "p_positivo": probs["Positivo"],
        })

    return pd.DataFrame(linhas)


# =========================================================
# 5. TIPO DA ISSUE COM ZERO-SHOT
# =========================================================

def classificar_tipo(textos, pipe_zero_shot):
    """
    Zero-shot multirrótulo: cada tipo recebe uma probabilidade própria
    (as três não precisam somar 1, porque uma issue pode ser bug e
    feature request ao mesmo tempo, como na etapa 1).
    """

    print("\nClassificando tipo da issue com zero-shot...")

    nomes = list(ROTULOS_ZERO_SHOT.keys())
    frases = list(ROTULOS_ZERO_SHOT.values())

    saidas = pipe_zero_shot(
        textos,
        candidate_labels=frases,
        hypothesis_template=TEMPLATE_ZERO_SHOT,
        multi_label=True,
        batch_size=TAMANHO_LOTE,
    )

    linhas = []
    for saida in saidas:
        # o modelo devolve os rótulos ordenados por score; volta para a nossa ordem
        por_frase = dict(zip(saida["labels"], saida["scores"]))
        linha = {}
        for nome, frase in zip(nomes, frases):
            score = por_frase[frase]
            linha[f"zs_{nome}"] = score
            linha[f"zs_{nome}_flag"] = "SIM" if score >= LIMIAR_ZERO_SHOT else "NÃO"
        linhas.append(linha)

    return pd.DataFrame(linhas)


# =========================================================
# 6. MONTAGEM E SALVAMENTO DOS RESULTADOS
# =========================================================

def montar_resultados(df, sentimento, tipo=None):
    """
    Junta identificação da issue, sentimento e (se houver) tipo.
    """

    base = df[["repositorio", "numero", "titulo", "idioma"]].reset_index(drop=True)
    partes = [base, sentimento.reset_index(drop=True)]
    if tipo is not None:
        partes.append(tipo.reset_index(drop=True))

    return pd.concat(partes, axis=1)


def salvar_resultados(res):
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    res.to_csv(ARQUIVO_RESULTADOS, index=False, encoding="utf-8-sig")
    print(f"\nResultados salvos em: {ARQUIVO_RESULTADOS}")


# =========================================================
# 7. COMPARAÇÃO COM A 1ª ETAPA
# =========================================================

def comparar_com_etapa1(res):
    """
    Compara o transformer com o léxico/Regex da 1ª etapa.

    Concordância não é acerto: dois métodos podem concordar e errar juntos.
    O que ela mostra é onde os métodos divergem, e é aí que vale ler as issues.
    """

    if not ARQUIVO_ETAPA1.exists():
        print(f"\n[!] {ARQUIVO_ETAPA1.name} não encontrado; rode a etapa 1 (python -m src.analise).")
        return None

    etapa1 = pd.read_csv(ARQUIVO_ETAPA1)
    etapa1 = etapa1[["repositorio", "numero", "bug", "divida_tecnica",
                     "feature_request", "sentimento"]].rename(
        columns={
            "sentimento": "sentimento_etapa1",
            "bug": "bug_etapa1",
            "divida_tecnica": "divida_tecnica_etapa1",
            "feature_request": "feature_request_etapa1",
        }
    )

    comp = res.merge(etapa1, on=["repositorio", "numero"], how="inner")
    comp["sentimento_concorda"] = comp["sentimento_etapa1"] == comp["sentimento_transformer"]

    print("\n" + "=" * 55)
    print("TRANSFORMER x ETAPA 1")
    print("=" * 55)
    print(f"\nIssues comparadas: {len(comp)}")
    print(f"Concordância no sentimento: {comp['sentimento_concorda'].mean() * 100:.1f}%")

    print("\nConcordância por repositório:")
    print((comp.groupby("repositorio")["sentimento_concorda"].mean() * 100).round(1).to_string())

    print("\nMatriz (linhas = etapa 1, colunas = transformer):")
    matriz = pd.crosstab(comp["sentimento_etapa1"], comp["sentimento_transformer"])
    print(matriz.reindex(index=CLASSES, columns=CLASSES, fill_value=0).to_string())

    if "zs_bug_flag" in comp.columns:
        print("\nTipo da issue (concordância etapa 1 x zero-shot):")
        for nome in ROTULOS_ZERO_SHOT:
            igual = (comp[f"{nome}_etapa1"] == comp[f"zs_{nome}_flag"]).mean() * 100
            print(f"  {nome}: {igual:.1f}%")

    comp.to_csv(ARQUIVO_COMPARACAO, index=False, encoding="utf-8-sig")
    print(f"\nComparação salva em: {ARQUIVO_COMPARACAO}")
    return comp


def gerar_grafico(comp):
    """
    Barras lado a lado: distribuição de sentimento da etapa 1 e do transformer.
    """

    etapa1 = comp["sentimento_etapa1"].value_counts().reindex(CLASSES, fill_value=0)
    transf = comp["sentimento_transformer"].value_counts().reindex(CLASSES, fill_value=0)

    fundo, texto = "#0E1117", "#F2F2F2"
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=fundo)
    ax.set_facecolor(fundo)

    posicoes = range(len(CLASSES))
    largura = 0.38
    ax.bar([p - largura / 2 for p in posicoes], etapa1.values, largura,
           label="Etapa 1 (léxico + spaCy)", color="#67E8F9")
    ax.bar([p + largura / 2 for p in posicoes], transf.values, largura,
           label="Etapa 2 (transformer)", color="#D946EF")

    for p, (a, b) in enumerate(zip(etapa1.values, transf.values)):
        ax.text(p - largura / 2, a + 2, str(a), ha="center", color=texto)
        ax.text(p + largura / 2, b + 2, str(b), ha="center", color=texto)

    ax.set_xticks(list(posicoes))
    ax.set_xticklabels(CLASSES, color=texto)
    ax.set_ylabel("Quantidade de issues", color=texto)
    ax.set_title("DevIssues - Sentimento: léxico x transformer", color=texto)
    ax.tick_params(colors=texto)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#444B57")
    ax.legend(facecolor="#1C1F26", edgecolor="#444B57", labelcolor=texto)

    fig.tight_layout()
    fig.savefig(ARQUIVO_GRAFICO, dpi=200, facecolor=fundo)
    plt.close(fig)
    print(f"Gráfico salvo em: {ARQUIVO_GRAFICO}")


# =========================================================
# 8. ROTULAGEM MANUAL (GABARITO)
# =========================================================

def gerar_amostra(forcar=False):
    """
    Cria a planilha de rotulagem: 15 issues por repositório, divididas
    entre as três integrantes.

    A planilha NÃO traz a previsão de nenhum método. Quem rotula não pode
    saber o que o léxico ou o transformer disseram, senão o gabarito
    fica contaminado.
    """

    if ARQUIVO_AMOSTRA.exists() and not forcar:
        print(f"\n[!] {ARQUIVO_AMOSTRA.name} já existe e pode ter rótulos preenchidos.")
        print("    Para recriar do zero, use --amostra --forcar.")
        return

    df = pd.read_csv(ARQUIVO_ENTRADA).fillna("")

    por_repositorio = [
        grupo.sample(n=min(ISSUES_POR_REPOSITORIO, len(grupo)), random_state=42)
        for _, grupo in df.groupby("repositorio")
    ]
    amostra = (
        pd.concat(por_repositorio)
        .sample(frac=1, random_state=42)  # embaralha, para ninguém rotular um repositório só
        .reset_index(drop=True)
    )

    amostra["rotulador"] = [INTEGRANTES[i % len(INTEGRANTES)] for i in range(len(amostra))]
    amostra["trecho"] = amostra["corpo"].astype(str).str.replace(r"\s+", " ", regex=True).str[:400]
    amostra["sentimento_manual"] = ""
    amostra["tipo_manual"] = ""

    amostra = amostra[["rotulador", "repositorio", "numero", "titulo", "trecho", "url",
                       "sentimento_manual", "tipo_manual"]]

    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    amostra.to_csv(ARQUIVO_AMOSTRA, index=False, encoding="utf-8-sig")

    print(f"\nPlanilha criada: {ARQUIVO_AMOSTRA}")
    print(amostra["rotulador"].value_counts().to_string())
    print("\nPreencha, em cada linha:")
    print("  sentimento_manual -> Positivo, Neutro ou Negativo")
    print("  tipo_manual       -> bug, divida_tecnica, feature_request, outro")
    print("                       (mais de um separado por ';', ex.: bug;feature_request)")


# =========================================================
# 9. AVALIAÇÃO CONTRA O GABARITO
# =========================================================

def _normalizar_sentimento_manual(valor):
    mapa = {"positivo": "Positivo", "neutro": "Neutro", "negativo": "Negativo"}
    return mapa.get(str(valor).strip().lower())


def avaliar():
    """
    Calcula acurácia e F1 macro do léxico (etapa 1) e do transformer
    contra os rótulos manuais, e precisão/revocação/F1 de cada tipo.
    """

    from sklearn.metrics import accuracy_score, classification_report, f1_score

    if not ARQUIVO_AMOSTRA.exists():
        raise FileNotFoundError("Rode primeiro: python -m src.transformers_sent --amostra")
    if not ARQUIVO_RESULTADOS.exists():
        raise FileNotFoundError("Rode primeiro: python -m src.transformers_sent")

    manual = pd.read_csv(ARQUIVO_AMOSTRA).fillna("")
    manual["sentimento_manual"] = manual["sentimento_manual"].map(_normalizar_sentimento_manual)
    preenchidas = manual.dropna(subset=["sentimento_manual"])

    print(f"\nRótulos de sentimento preenchidos: {len(preenchidas)} de {len(manual)}")
    if preenchidas.empty:
        print("[!] Nenhum rótulo válido ainda.")
        return None
    if len(preenchidas) < len(manual):
        print("[!] Avaliando só as linhas preenchidas (valores aceitos: Positivo, Neutro, Negativo).")

    comp = pd.read_csv(ARQUIVO_COMPARACAO) if ARQUIVO_COMPARACAO.exists() else None
    if comp is None:
        raise FileNotFoundError("Faltou a comparação com a etapa 1 (relatorio_final.csv).")

    junto = preenchidas.merge(
        comp[["repositorio", "numero", "sentimento_etapa1", "sentimento_transformer"]
             + [c for c in comp.columns if c.startswith("zs_") and c.endswith("_flag")]
             + [c for c in comp.columns if c.endswith("_etapa1") and c != "sentimento_etapa1"]],
        on=["repositorio", "numero"], how="inner",
    )

    linhas = []
    print("\n" + "=" * 55)
    print("AVALIAÇÃO DO SENTIMENTO (vs. rótulo manual)")
    print("=" * 55)
    for nome, coluna in [("Etapa 1 (léxico)", "sentimento_etapa1"),
                         ("Transformer", "sentimento_transformer")]:
        acc = accuracy_score(junto["sentimento_manual"], junto[coluna])
        f1 = f1_score(junto["sentimento_manual"], junto[coluna],
                      average="macro", labels=CLASSES, zero_division=0)
        print(f"\n{nome}: acurácia {acc * 100:.1f}% | F1 macro {f1:.3f}")
        print(classification_report(junto["sentimento_manual"], junto[coluna],
                                    labels=CLASSES, zero_division=0))
        linhas.append({"tarefa": "sentimento", "metodo": nome, "item": "geral",
                       "acuracia": acc, "f1": f1, "n": len(junto)})

    # Tipo da issue: um problema binário por rótulo
    tipos = manual[manual["tipo_manual"].astype(str).str.strip() != ""]
    if not tipos.empty and any(c.startswith("zs_") for c in comp.columns):
        tipos = tipos.merge(comp, on=["repositorio", "numero"], how="inner")
        print("\n" + "=" * 55)
        print(f"AVALIAÇÃO DO TIPO (vs. rótulo manual, {len(tipos)} issues)")
        print("=" * 55)
        for nome in ROTULOS_ZERO_SHOT:
            real = tipos["tipo_manual"].str.lower().str.contains(nome)
            for metodo, coluna in [("Etapa 1 (Regex)", f"{nome}_etapa1"),
                                   ("Zero-shot", f"zs_{nome}_flag")]:
                previsto = tipos[coluna] == "SIM"
                tp = int((real & previsto).sum())
                prec = tp / previsto.sum() if previsto.sum() else 0.0
                rev = tp / real.sum() if real.sum() else 0.0
                f1 = 2 * prec * rev / (prec + rev) if (prec + rev) else 0.0
                print(f"{nome:16} {metodo:16} precisão {prec:.2f} | revocação {rev:.2f} | F1 {f1:.2f}")
                linhas.append({"tarefa": "tipo", "metodo": metodo, "item": nome,
                               "acuracia": (real == previsto).mean(), "f1": f1, "n": len(tipos)})

    pd.DataFrame(linhas).to_csv(ARQUIVO_AVALIACAO, index=False, encoding="utf-8-sig")
    print(f"\nAvaliação salva em: {ARQUIVO_AVALIACAO}")
    return junto


# =========================================================
# 10. EXECUÇÃO PRINCIPAL
# =========================================================

def main():
    parser = argparse.ArgumentParser(description="DevIssues - Trilha C: transformers")
    parser.add_argument("--amostra", action="store_true", help="gera a planilha de rotulagem manual")
    parser.add_argument("--forcar", action="store_true", help="com --amostra, recria mesmo se já existir")
    parser.add_argument("--avaliar", action="store_true", help="métricas contra os rótulos manuais")
    parser.add_argument("--sem-tipo", action="store_true", help="pula o zero-shot (mais rápido)")
    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("DEVISSUES - TRILHA C: TRANSFORMERS")
    print("=" * 55)

    if args.amostra:
        gerar_amostra(forcar=args.forcar)
        return
    if args.avaliar:
        avaliar()
        return

    df = carregar_issues()
    pipe_sentimento, pipe_zero_shot = carregar_pipelines(com_tipo=not args.sem_tipo)

    textos = df["texto"].tolist()
    sentimento = classificar_sentimento(textos, pipe_sentimento)
    tipo = classificar_tipo(textos, pipe_zero_shot) if pipe_zero_shot else None

    res = montar_resultados(df, sentimento, tipo)
    salvar_resultados(res)

    comp = comparar_com_etapa1(res)
    if comp is not None:
        gerar_grafico(comp)

    print("\nPipeline de transformers finalizado!")


if __name__ == "__main__":
    main()
