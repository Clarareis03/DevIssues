"""
DevIssues — Dashboard & Metodologia Técnica (Página Única)
"""

import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# Tenta importar a análise para processar em memória caso o relatório final ainda não exita
try:
    from src.analise import executar_analise_completa
except ModuleNotFoundError:
    executar_analise_completa = None

# 1. Configuração da Página
st.set_page_config(
    page_title="DevIssues — Dashboard & Metodologia",
    page_icon="🔍",
    layout="wide",
)

# Cores fixas para as categorias, usadas em todos os gráficos Plotly
CORES_SENTIMENTO = {"Positivo": "#22c55e", "Neutro": "#facc15", "Negativo": "#ef4444"}
CORES_CATEGORIA = {
    "Bugs": "#ef4444",
    "Dívida Técnica": "#f59e0b",
    "Feature Requests": "#3b82f6",
    "Urgência": "#a855f7",
}


def estilizar(fig, altura=340):
    """Aplica um visual consistente e transparente aos gráficos Plotly,
    para se encaixarem bem no tema escuro do dashboard."""
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#f2f2f2",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


@st.cache_data
def carregar_dados():
    """Carrega o relatório final consolidado ou executa a análise se necessário."""
    caminho_relatorio = Path("resultados/relatorio_final.csv")

    if caminho_relatorio.exists():
        return pd.read_csv(caminho_relatorio)

    # Se o relatório não existir, tenta gerar automaticamente
    caminho_dados = Path("dados/issues.csv")
    if caminho_dados.exists() and executar_analise_completa:
        executar_analise_completa()
        if caminho_relatorio.exists():
            return pd.read_csv(caminho_relatorio)

    return None


# Carrega a base
df = carregar_dados()

# ---------------------------------------------------------
# CABEÇALHO PRINCIPAL
# ---------------------------------------------------------
st.title("🔍 DevIssues — Dashboard & Metodologia de Análise")
st.markdown(
    "Análise linguística e categorização automática de *issues* do GitHub utilizando **Regex** e **NLP (spaCy)**."
)
st.divider()

if df is None or df.empty:
    st.error(
        "⚠️ Nenhum dado encontrado em `resultados/relatorio_final.csv` ou `dados/issues.csv`. Certifique-se de que a base coletada está na pasta do projeto."
    )
    st.stop()

# ---------------------------------------------------------
# SEÇÃO 1: DASHBOARD & MÉTRICAS (RESULTADOS)
# ---------------------------------------------------------
st.header("📊 1. Resultados & Analytics")

total = len(df)
bugs = len(df[df["bug"] == "SIM"])
divida = len(df[df["divida_tecnica"] == "SIM"])
feature = len(df[df["feature_request"] == "SIM"])
urgente = len(df[df["urgencia"] == "SIM"])
n_repos = df["repositorio"].nunique()

# Faixa de destaque com os números-chave, antes das métricas detalhadas
st.markdown(
    f"""
    <div style="background:#1c1f26;border-radius:0.8rem;padding:1rem 1.5rem;margin-bottom:1rem;">
        <span style="font-size:1.4rem;font-weight:700;color:#f2f2f2;">
            {total} issues analisadas em {n_repos} repositórios · {urgente} marcadas como urgentes
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Cartões de Métricas
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total de Issues", total)
m2.metric(" Bugs / Erros", f"{bugs}", f"{(bugs/total)*100:.1f}%")
m3.metric(" Dívida Técnica", f"{divida}", f"{(divida/total)*100:.1f}%")
m4.metric(" Feature Requests", f"{feature}", f"{(feature/total)*100:.1f}%")
m5.metric(" Urgentes", f"{urgente}", f"{(urgente/total)*100:.1f}%")

st.write("")

# Gráficos Visuais (Plotly, no lugar do st.bar_chart padrão)
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Análise de Sentimento (Lemas spaCy)")
    sent_df = df["sentimento"].value_counts().reset_index()
    sent_df.columns = ["Sentimento", "Quantidade"]
    fig_sent = px.pie(
        sent_df,
        values="Quantidade",
        names="Sentimento",
        color="Sentimento",
        color_discrete_map=CORES_SENTIMENTO,
        hole=0.45,
    )
    st.plotly_chart(estilizar(fig_sent), use_container_width=True)

with col_g2:
    st.subheader("Distribuição por Categoria")
    cats_df = pd.DataFrame(
        {
            "Categoria": ["Bugs", "Dívida Técnica", "Feature Requests", "Urgência"],
            "Quantidade": [bugs, divida, feature, urgente],
        }
    )
    fig_cats = px.bar(
        cats_df,
        x="Categoria",
        y="Quantidade",
        color="Categoria",
        color_discrete_map=CORES_CATEGORIA,
        text="Quantidade",
    )
    fig_cats.update_traces(textposition="outside")
    fig_cats.update_layout(showlegend=False)
    st.plotly_chart(estilizar(fig_cats), use_container_width=True)

# Comparativo entre repositórios
st.subheader("🗂️ Comparativo por Repositório")

comparativo = (
    df.groupby("repositorio")
    .agg(
        Bugs=("bug", lambda s: (s == "SIM").sum()),
        **{"Dívida Técnica": ("divida_tecnica", lambda s: (s == "SIM").sum())},
        **{"Feature Requests": ("feature_request", lambda s: (s == "SIM").sum())},
        Urgência=("urgencia", lambda s: (s == "SIM").sum()),
    )
    .reset_index()
)

comparativo_longo = comparativo.melt(
    id_vars="repositorio", var_name="Categoria", value_name="Quantidade"
)

fig_repo = px.bar(
    comparativo_longo,
    x="repositorio",
    y="Quantidade",
    color="Categoria",
    barmode="group",
    color_discrete_map=CORES_CATEGORIA,
)
fig_repo.update_layout(xaxis_title="", legend_title="")
st.plotly_chart(estilizar(fig_repo, altura=380), use_container_width=True)

# Explorador de Tabela com Filtros
st.write("")
st.subheader(" Explorar Base de Dados Processada")

f_col1, f_col2 = st.columns(2)
with f_col1:
    filtro_cat = st.selectbox(
        "Filtrar Categoria:",
        ["Todas", "Bugs", "Dívida Técnica", "Feature Requests", "Urgência"],
    )
with f_col2:
    filtro_sent = st.selectbox(
        "Filtrar Sentimento:", ["Todos", "Positivo", "Neutro", "Negativo"]
    )

df_exibicao = df.copy()
if filtro_cat == "Bugs":
    df_exibicao = df_exibicao[df_exibicao["bug"] == "SIM"]
elif filtro_cat == "Dívida Técnica":
    df_exibicao = df_exibicao[df_exibicao["divida_tecnica"] == "SIM"]
elif filtro_cat == "Feature Requests":
    df_exibicao = df_exibicao[df_exibicao["feature_request"] == "SIM"]
elif filtro_cat == "Urgência":
    df_exibicao = df_exibicao[df_exibicao["urgencia"] == "SIM"]

if filtro_sent != "Todos":
    df_exibicao = df_exibicao[df_exibicao["sentimento"] == filtro_sent]

st.dataframe(
    df_exibicao[
        [
            "numero",
            "repositorio",
            "titulo",
            "sentimento",
            "bug",
            "divida_tecnica",
            "urgencia",
            "erros_encontrados",
            "versoes_encontradas",
        ]
    ],
    use_container_width=True,
    height=280,
)

st.divider()

# ---------------------------------------------------------
# SEÇÃO 2: METODOLOGIA TÉCNICA E PIPELINE
# ---------------------------------------------------------
st.header("⚙️ 2. Arquitetura e Metodologia do Projeto")
st.markdown(
    "Abaixo está detalhada a pipeline de processamento desenvolvida por cada integrante da equipe."
)

tab_coleta, tab_regex, tab_spacy, tab_integracao = st.tabs(
    [
        " 1. Coleta de Dados (Pessoa 1)",
        " 2. Expressões Regulares (Pessoa 2)",
        " 3. Processamento NLP / spaCy (Pessoa 2)",
        " 4. Consolidação & Regras (Pessoa 3)",
    ]
)

with tab_coleta:
    st.markdown("""
    ###  Coleta de Dados via REST API do GitHub
    - **Fonte dos Dados:** Repositórios públicos do GitHub .
    - **Endpoint:** `GET /repos/{owner}/{repo}/issues`.
    - **Campos Extraídos:** Número da issue, título, corpo da descrição (*body*), labels originais, estado (*open/closed*), datas de criação/fecho e URL.
    - **Tratamento:** Filtro de paginação para contornar limites da API e exportação limpa em formato CSV em `dados/issues.csv`.
    """)

with tab_regex:
    st.markdown("""
    ### 🎯 Expressões Regulares (Regex)
    O módulo `src/regex.py` aplica padrões regex específicos sobre o texto combinado (*Título + Corpo*) de cada issue para capturar metadados técnicos:

    1. **Erros e Exceções:** Padrões para capturar exceções da linguagem (ex: `\\b[A-Za-z_]\\w*(?:Error|Exception)\\b`).
    2. **Versões de Software:** Captura de padrões como `v1.2.3`, `Python 3.10` ou `v2.0-beta`, com filtros de contexto para evitar confundir com IPs, percentuais e métricas.
    3. **Termos de Urgência:** Expressões como `urgent`, `critical`, `blocker`, `asap`.
    4. **Caminhos de Ficheiros e URLs:** Identificação de referências de código e links para relatórios externos.
    """)

with tab_spacy:
    st.markdown("""
    ### 🧠 Processamento de Linguagem Natural (spaCy)
    O módulo `src/nlp.py` utiliza os modelos de linguagem `en_core_web_sm` (Inglês) e `pt_core_news_sm` (Português) para realizar:

    - **Lematização:** Redução de palavras à sua forma base (ex: *buggy*, *bugs* $\\rightarrow$ `bug`; *failed*, *failing* $\\rightarrow$ `fail`).
    - **Filtragem de Stopwords & Pontuação:** Remoção de termos ruído para focar apenas em tokens com valor semântico.
    - **Detecção de Entidades (NER):** Identificação automática de organizações, datas e nomes mencionados no texto.
    """)

with tab_integracao:
    st.markdown("""
    ### 📊 Regras de Classificação e Sentimento
    O módulo `src/analise.py` consome os retornos do Regex e do spaCy para tomar as decisões finais:

    - **Classificação de Categorias:** Combinando labels do GitHub, capturas de Regex e lemas do spaCy para marcar flags de **Bug**, **Dívida Técnica**, **Feature Request** e **Urgência**.
    - **Análise de Sentimento:** Baseada na contagem e polaridade dos lemas extraídos pelo spaCy (comparação entre lemas de satisfação e lemas de frustração/falha).
    - **Relatório Consolidado:** Geração automática do ficheiro `resultados/relatorio_final.csv`.
    """)

st.write("")
st.caption("DevIssues — Projeto desenvolvido para a disciplina de Processamento de Linguagem Natural e Engenharia de Software.")