from pathlib import Path
import html

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
RESULTADOS = ROOT / "resultados"
ROXO = "#8B5CF6"
LAVANDA = "#B9A4FF"
CIANO = "#39D6E7"
ROSA = "#F472B6"
VERDE = "#34D399"
AMARELO = "#FBBF24"
PALETA = [ROXO, CIANO, ROSA, VERDE, AMARELO, "#818CF8"]
SENTIMENTOS = {"Positivo": VERDE, "Neutro": "#94A3B8", "Negativo": ROSA}

st.set_page_config(page_title="DevIssues | Intelligence Studio", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--purple:#8B5CF6;--lavender:#B9A4FF;--ink:#080B15;}
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif;}
.stApp{background:radial-gradient(ellipse 58% 42% at 84% 0%,rgba(111,64,220,.15),transparent 75%),radial-gradient(ellipse 30% 25% at 0% 60%,rgba(31,160,185,.06),transparent 80%),#080B15;color:#EEF1FF;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#121426 0%,#0D1020 100%);border-right:1px solid rgba(168,149,255,.12);}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#A7ACC6;}
[data-testid="stSidebar"] .stRadio label{border-radius:12px;padding:9px 12px;transition:.2s;}
[data-testid="stSidebar"] .stRadio label:hover{background:rgba(139,92,246,.1);}
.block-container{max-width:1320px;padding:2rem 3.5rem 4rem;}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em;}
h1{font-weight:700!important;}
h3{font-size:1.23rem!important;}
[data-testid="stMetric"]{background:linear-gradient(150deg,rgba(23,27,49,.92),rgba(14,18,34,.96));border:1px solid rgba(172,159,250,.14);border-radius:18px;padding:20px 20px;min-height:118px;}
[data-testid="stMetricLabel"]{color:#A4A9C3;font-size:.85rem;}
[data-testid="stMetricValue"]{font-family:'Space Grotesk';color:#F6F3FF;font-weight:700;}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:rgba(172,159,250,.15)!important;}
[data-testid="stDataFrame"]{border:1px solid rgba(172,159,250,.16);border-radius:14px;overflow:hidden;}
[data-testid="stExpander"]{background:#101426;border:1px solid rgba(172,159,250,.13);border-radius:14px;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:10px;}
[data-testid="stTabs"] button[role="tab"]{border-radius:9px;color:#B4B8CE;}
[data-testid="stTabs"] button[aria-selected="true"]{color:#D7C8FF;border-bottom-color:#8B5CF6;}
.stButton>button[kind="primary"]{background:linear-gradient(110deg,#7C3AED,#A855F7);color:white;border:0;border-radius:12px;font-weight:700;box-shadow:0 8px 30px rgba(124,58,237,.19);}
.stButton>button{border-radius:12px;}
[data-testid="stAlert"]{border-radius:14px;}
.hero{border:1px solid rgba(177,148,255,.23);border-radius:24px;padding:34px 38px;background:radial-gradient(circle at 87% 27%,rgba(133,85,255,.29),transparent 35%),linear-gradient(112deg,#191632,#11182A 68%,#13203A);position:relative;overflow:hidden;margin-bottom:24px;}
.eyebrow{color:#BDB1FE;font-size:.72rem;font-weight:800;letter-spacing:.19em;text-transform:uppercase;margin-bottom:12px;}
.hero h1{font-size:clamp(2rem,4vw,3.4rem);margin:0 0 8px;line-height:1.08;color:#FAF9FF;}
.hero p{color:#ADB7D2;max-width:650px;margin:0;font-size:1rem;line-height:1.65;}
.hero strong{color:#DDD5FF;}
.section-label{font-size:.73rem;letter-spacing:.15em;font-weight:800;color:#A7A0C7;margin:20px 0 9px;text-transform:uppercase;}
.section-intro{color:#A7ADC7;font-size:.95rem;margin-top:-5px;margin-bottom:14px;}
.tag{display:inline-block;background:rgba(139,92,246,.17);border:1px solid rgba(171,145,255,.26);border-radius:999px;padding:5px 12px;color:#D1C2FF;font-size:.75rem;font-weight:700;letter-spacing:.02em;}
.mini{background:linear-gradient(155deg,#181B31,#111525);border:1px solid rgba(167,153,241,.13);padding:19px 20px;border-radius:17px;min-height:124px;}
.mini .num{font-family:'Space Grotesk';font-size:1.65rem;font-weight:700;color:#F6F2FF;line-height:1.4;}
.mini .name{font-size:.79rem;color:#A8ADC4;font-weight:600;}
.footer{color:#69738E;font-size:.74rem;padding-top:22px;text-align:center;letter-spacing:.05em;}
@media(max-width:850px){.block-container{padding:1.4rem 1rem 3rem}.hero{padding:24px 22px}}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def ler_csv(nome):
    arquivo = RESULTADOS / nome
    if not arquivo.is_file():
        return None
    return pd.read_csv(arquivo, encoding="utf-8-sig")

@st.cache_data(show_spinner=False)
def ler_vetores():
    return np.load(RESULTADOS / "embeddings.npy")

@st.cache_resource(show_spinner=False)
def modelo_busca():
    from src.embeddings import carregar_modelo
    return carregar_modelo()


def plot_estilo(fig, altura=365):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="DM Sans", color="#CCD3E8", size=12),
        height=altura, margin=dict(l=12, r=12, t=28, b=25),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
        xaxis=dict(showgrid=False, zeroline=False, linecolor="rgba(160,166,210,.16)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(160,166,210,.09)", zeroline=False),
    )
    return fig


def grafico_barras(tabela, x, y, cor=ROXO, horizontal=False, altura=350):
    fig = px.bar(tabela, x=y if horizontal else x, y=x if horizontal else y,
                 orientation="h" if horizontal else "v", text=y,
                 color_discrete_sequence=[cor])
    fig.update_traces(textposition="outside", marker_line_width=0, cliponaxis=False)
    if horizontal:
        fig.update_layout(yaxis=dict(categoryorder="total ascending", showgrid=False))
    st.plotly_chart(plot_estilo(fig, altura), use_container_width=True, config={"displayModeBar": False})


def mini(valor, titulo):
    return f'<div class="mini"><div class="num">{html.escape(str(valor))}</div><div class="name">{html.escape(titulo)}</div></div>'


def titulo_secao(titulo, descricao=None):
    st.subheader(titulo)
    if descricao:
        st.markdown(f'<p class="section-intro">{html.escape(descricao)}</p>', unsafe_allow_html=True)


def mostrar_tabela(df, colunas, titulo="Explorar registros"):
    visiveis = [c for c in colunas if c in df.columns]
    if visiveis:
        with st.expander(f"{titulo} · {len(df)} registros"):
            st.dataframe(df[visiveis], use_container_width=True, hide_index=True, height=360)


def contagem_termos(serie):
    valores = (serie.fillna("").astype(str).str.split(";").explode().str.strip().str.lower())
    return valores[valores.ne("")].value_counts()


principal = ler_csv("relatorio_final.csv")
spacy = ler_csv("spacy_avancado.csv")
spacy_regex = ler_csv("spacy_vs_regex.csv")
embeddings = ler_csv("embeddings_resultados.csv")
transformers = ler_csv("transformers_resultados.csv")
comparacao = ler_csv("transformers_vs_etapa1.csv")
avaliacao = ler_csv("avaliacao_transformers.csv")

with st.sidebar:
    st.markdown("<div style='font-family:Space Grotesk;font-weight:700;font-size:1.55rem;padding:18px 0 5px'>✦ DevIssues</div>", unsafe_allow_html=True)
    st.caption("INTELLIGENCE STUDIO")
    st.write("")
    pagina = st.radio("EXPLORAR", ["Visão geral", "spaCy avançado", "Embeddings", "Transformers"], label_visibility="visible")
    st.divider()
    st.markdown('<div class="eyebrow">DATASET</div>', unsafe_allow_html=True)
    st.markdown(f"<div style='font-family:Space Grotesk;font-size:2rem;font-weight:700'>{len(principal) if principal is not None else '—'}</div><div style='color:#9EA8C3;font-size:.82rem'>issues analisadas</div>", unsafe_allow_html=True)
    st.write("")
    st.markdown('<span class="tag">ETAPA 02 · NLP AVANÇADO</span>', unsafe_allow_html=True)

subtitulos = {
    "Visão geral": ("Inteligência em cada issue.", "Da linguagem natural aos padrões que revelam como projetos open source evoluem."),
    "spaCy avançado": ("Além das palavras.", "Entidades, tecnologias e precisão linguística em cada issue."),
    "Embeddings": ("Textos que se conectam.", "Representações vetoriais, clusters e descoberta semântica."),
    "Transformers": ("O contexto muda tudo.", "Sentimentos e classificação zero-shot em uma nova perspectiva."),
}
frase, apoio = subtitulos[pagina]
st.markdown(f'<div class="hero"><div class="eyebrow">DEVISSUES / {html.escape(pagina.upper())}</div><h1>{html.escape(frase)}</h1><p>{html.escape(apoio)}</p></div>', unsafe_allow_html=True)

if pagina == "Visão geral":
    if principal is None:
        st.error("A base principal não foi encontrada em resultados/relatorio_final.csv.")
        st.stop()
    n_repos = principal["repositorio"].nunique()
    n_bugs = int(principal["bug"].eq("SIM").sum())
    n_features = int(principal["feature_request"].eq("SIM").sum())
    n_dividas = int(principal["divida_tecnica"].eq("SIM").sum())
    n_urgentes = int(principal["urgencia"].eq("SIM").sum())
    cols = st.columns(5)
    for col, (numero, rotulo) in zip(cols, [(len(principal), "Issues"), (n_repos, "Repositórios"), (n_bugs, "Bugs"), (n_features, "Funcionalidades"), (n_dividas, "Dívida técnica")]):
        col.markdown(mini(numero, rotulo), unsafe_allow_html=True)
    st.write("")
    esquerda, direita = st.columns([1, 1.2], gap="large")
    with esquerda:
        titulo_secao("Panorama de sentimentos")
        s = principal["sentimento"].fillna("Não identificado").value_counts().reset_index()
        s.columns = ["Sentimento", "Quantidade"]
        fig = px.pie(s, names="Sentimento", values="Quantidade", hole=.70,
                     color="Sentimento", color_discrete_map=SENTIMENTOS)
        fig.update_traces(textinfo="percent", textposition="outside", marker=dict(line=dict(color="#0D1020", width=3)))
        fig.add_annotation(text=f"<b>{len(principal)}</b><br><span style='font-size:11px'>issues</span>", x=.5, y=.5, showarrow=False, font=dict(size=22, color="#F6F2FF"))
        st.plotly_chart(plot_estilo(fig), use_container_width=True, config={"displayModeBar": False})
    with direita:
        titulo_secao("Categorias em destaque")
        cat = pd.DataFrame({"Categoria": ["Bugs", "Funcionalidades", "Dívida técnica", "Urgência"],
                            "Quantidade": [n_bugs, n_features, n_dividas, n_urgentes]})
        grafico_barras(cat, "Categoria", "Quantidade", horizontal=True)
    titulo_secao("Pulso dos repositórios", "Categorias não são exclusivas: uma issue pode pertencer a mais de uma.")
    categorias = {"bug": "Bug", "feature_request": "Funcionalidade", "divida_tecnica": "Dívida técnica", "urgencia": "Urgência"}
    linhas = []
    for repo, grupo in principal.groupby("repositorio"):
        for coluna, rotulo in categorias.items():
            linhas.append({"Repositório": repo, "Categoria": rotulo, "Issues": int(grupo[coluna].eq("SIM").sum())})
    por_repo = pd.DataFrame(linhas)
    fig = px.bar(por_repo, x="Repositório", y="Issues", color="Categoria", barmode="group",
                 color_discrete_sequence=PALETA)
    st.plotly_chart(plot_estilo(fig, 365), use_container_width=True, config={"displayModeBar": False})
    mostrar_tabela(principal, ["repositorio", "numero", "titulo", "sentimento", "bug", "feature_request", "divida_tecnica", "urgencia"], "Consultar base")

elif pagina == "spaCy avançado":
    if spacy is None:
        st.error("Os resultados de spaCy não foram encontrados.")
        st.stop()
    c1, c2, c3, c4 = st.columns(4)
    metricas = [(len(spacy), "Issues processadas")]
    for coluna, rotulo in [("erros", "Com erros"), ("bibliotecas", "Com bibliotecas"), ("tecnologias", "Com tecnologias")]:
        metricas.append((int(spacy[coluna].fillna("").astype(str).str.strip().ne("").sum()) if coluna in spacy else 0, rotulo))
    for c, (numero, rotulo) in zip([c1,c2,c3,c4], metricas):
        c.markdown(mini(numero, rotulo), unsafe_allow_html=True)
    st.write("")
    col_repo, col_tipo = st.columns([1, 1])
    with col_repo:
        repo = st.selectbox("Repositório", ["Todos"] + sorted(spacy["repositorio"].dropna().unique().tolist()))
    with col_tipo:
        campo = st.selectbox("Explorar entidades", ["bibliotecas", "tecnologias", "erros", "versoes"], format_func=lambda x: {"bibliotecas":"Bibliotecas", "tecnologias":"Tecnologias", "erros":"Erros", "versoes":"Versões"}[x])
    filtrado = spacy if repo == "Todos" else spacy[spacy["repositorio"] == repo]
    st.write("")
    titulo_secao("Entidades mais frequentes")
    frequencias = contagem_termos(filtrado[campo]) if campo in filtrado else pd.Series(dtype=int)
    if frequencias.empty:
        st.info("Nenhuma entidade encontrada neste recorte.")
    else:
        top = frequencias.head(12).reset_index()
        top.columns = ["Entidade", "Ocorrências"]
        grafico_barras(top.sort_values("Ocorrências"), "Entidade", "Ocorrências", cor=CIANO, horizontal=True, altura=390)
    if spacy_regex is not None and {"status_erros", "status_versoes"}.issubset(spacy_regex.columns):
        titulo_secao("spaCy × Regex", "Comparação de resultados por issue: concordância não equivale à precisão.")
        a, b = st.columns(2, gap="large")
        for coluna, area in [("status_erros", a), ("status_versoes", b)]:
            with area:
                st.markdown("**Erros**" if coluna == "status_erros" else "**Versões**")
                resumo = spacy_regex[coluna].fillna("Não definido").value_counts().reset_index()
                resumo.columns = ["Status", "Quantidade"]
                grafico_barras(resumo, "Status", "Quantidade", cor=LAVANDA, altura=285)
    mostrar_tabela(filtrado, ["repositorio", "numero", "titulo", "erros", "versoes", "bibliotecas", "tecnologias", "vizinhas"], "Explorar entidades por issue")

elif pagina == "Embeddings":
    if embeddings is None:
        st.error("Os resultados de embeddings não foram encontrados.")
        st.stop()
    if "cluster" not in embeddings:
        st.error("A coluna cluster não foi encontrada nos resultados.")
        st.stop()
    c1, c2, c3 = st.columns(3)
    for c,(numero,rotulo) in zip([c1,c2,c3], [(len(embeddings), "Issues vetorizadas"), (embeddings["cluster"].nunique(), "Clusters"), ("384", "Dimensões do modelo")]):
        c.markdown(mini(numero,rotulo),unsafe_allow_html=True)
    st.write("")
    titulo_secao("Mapa semântico", "Projeção PCA em duas dimensões; distâncias na projeção não representam toda a informação dos vetores.")
    if {"pca_1", "pca_2"}.issubset(embeddings.columns):
        dados_plot = embeddings.copy()
        dados_plot["Grupo"] = "Cluster " + dados_plot["cluster"].astype(str)
        fig = px.scatter(dados_plot, x="pca_1", y="pca_2", color="Grupo", hover_name="titulo" if "titulo" in dados_plot else None,
                         hover_data=[c for c in ["repositorio", "numero"] if c in dados_plot], color_discrete_sequence=PALETA, opacity=.78)
        fig.update_traces(marker=dict(size=9, line=dict(width=.5,color="rgba(255,255,255,.25)")))
        fig.update_layout(xaxis_title="Componente principal 1", yaxis_title="Componente principal 2")
        st.plotly_chart(plot_estilo(fig, 460), use_container_width=True, config={"displayModeBar": False})
    elif (RESULTADOS / "clusters_pca.png").exists():
        st.image(str(RESULTADOS / "clusters_pca.png"), use_container_width=True)
    distribuicao = embeddings["cluster"].value_counts().sort_index().reset_index()
    distribuicao.columns = ["Cluster", "Quantidade"]
    col_grafico, col_filtro = st.columns([1.2, 1], gap="large")
    with col_grafico:
        titulo_secao("Distribuição dos grupos")
        distribuicao["Cluster"] = "Cluster " + distribuicao["Cluster"].astype(str)
        grafico_barras(distribuicao, "Cluster", "Quantidade", cor=ROXO, altura=310)
    with col_filtro:
        titulo_secao("Explore os grupos")
        selecao = st.selectbox("Cluster", ["Todos"] + sorted(embeddings["cluster"].dropna().unique().tolist()), format_func=lambda x: "Todos os clusters" if x == "Todos" else f"Cluster {x}")
        grupo = embeddings if selecao == "Todos" else embeddings[embeddings["cluster"] == selecao]
        st.metric("Issues no recorte", len(grupo))
        st.caption("Agrupamentos calculados com KMeans sobre embeddings multilíngues.")
    mostrar_tabela(grupo, ["repositorio", "numero", "titulo", "cluster", "pca_1", "pca_2"], "Ver issues agrupadas")
    st.divider()
    titulo_secao("Busca semântica", "Pesquise em linguagem natural e encontre issues semanticamente próximas.")
    consulta = st.text_input("Descreva um problema", placeholder="Ex.: Error when connecting to database")
    if st.button("Encontrar issues semelhantes", type="primary", use_container_width=False):
        if not consulta.strip():
            st.warning("Digite uma descrição para pesquisar.")
        elif not (RESULTADOS / "embeddings.npy").exists():
            st.error("O arquivo de vetores não foi encontrado.")
        else:
            try:
                with st.spinner("Explorando conexões semânticas..."):
                    from src.embeddings import carregar_issues, buscar_issues_semelhantes
                    base = carregar_issues()
                    vetores = ler_vetores()
                    identificadores_base = list(zip(base["repositorio"].astype(str), base["numero"].astype(str)))
                    identificadores_resultados = list(zip(embeddings["repositorio"].astype(str), embeddings["numero"].astype(str)))
                    if len(vetores) != len(base) or identificadores_base != identificadores_resultados:
                        st.error("A ordem dos vetores não corresponde à base atual. Regenere os embeddings antes da busca.")
                    else:
                        modelo = modelo_busca()
                        achados = buscar_issues_semelhantes(consulta, modelo, vetores, base, top_k=5)
                        achados = achados.copy()
                        achados["similaridade"] = (achados["similaridade"] * 100).round(1)
                        achados = achados.rename(columns={"repositorio":"Repositório", "numero":"Issue", "titulo":"Título", "similaridade":"Similaridade (%)"})
                        st.dataframe(achados, use_container_width=True, hide_index=True)
                        st.caption("A similaridade indica proximidade entre textos, não certeza de relevância.")
            except ImportError:
                st.error("Para ativar a busca, instale as dependências com: python -m pip install -r requirements.txt")
            except Exception as exc:
                st.error(f"Não foi possível realizar a busca: {exc}")

elif pagina == "Transformers":
    if transformers is None:
        st.error("Os resultados dos Transformers não foram encontrados.")
        st.stop()
    c1,c2,c3 = st.columns(3)
    classes = transformers["sentimento_transformer"].nunique() if "sentimento_transformer" in transformers else 0
    confianca = (transformers["confianca_sentimento"].mean()*100) if "confianca_sentimento" in transformers else None
    metricas = [(len(transformers), "Issues classificadas"), (classes, "Classes de sentimento"), (f"{confianca:.1f}%" if confianca is not None else "—", "Confiança média do modelo")]
    for c,(numero,rotulo) in zip([c1,c2,c3], metricas):
        c.markdown(mini(numero,rotulo), unsafe_allow_html=True)
    st.write("")
    titulo_secao("Sentimento com Transformer")
    if "sentimento_transformer" in transformers:
        dist = transformers["sentimento_transformer"].value_counts().reset_index()
        dist.columns = ["Sentimento", "Quantidade"]
        fig = px.bar(dist, x="Sentimento", y="Quantidade", text="Quantidade", color="Sentimento", color_discrete_map=SENTIMENTOS)
        fig.update_traces(textposition="outside",marker_line_width=0)
        fig.update_layout(showlegend=False)
        st.plotly_chart(plot_estilo(fig, 340),use_container_width=True,config={"displayModeBar":False})
    if comparacao is not None and {"sentimento_etapa1", "sentimento_transformer"}.issubset(comparacao.columns):
        titulo_secao("Evolução da análise", "Comparação entre léxico spaCy e Transformer para as mesmas issues.")
        plot = comparacao[["sentimento_etapa1", "sentimento_transformer"]].melt(var_name="Método",value_name="Sentimento")
        plot["Método"] = plot["Método"].map({"sentimento_etapa1":"Léxico + spaCy", "sentimento_transformer":"Transformer"})
        qtd = plot.groupby(["Método", "Sentimento"]).size().reset_index(name="Issues")
        fig=px.bar(qtd,x="Sentimento",y="Issues",color="Método",barmode="group",text="Issues",color_discrete_sequence=[CIANO,ROXO],category_orders={"Sentimento":["Negativo","Neutro","Positivo"]})
        fig.update_traces(textposition="outside")
        st.plotly_chart(plot_estilo(fig, 345),use_container_width=True,config={"displayModeBar":False})
        concorda = (comparacao["sentimento_etapa1"].astype(str) == comparacao["sentimento_transformer"].astype(str)).mean()*100
        st.metric("Concordância entre métodos",f"{concorda:.1f}%")
        st.caption("Concordância não mede acurácia; para isso é necessário comparar com rótulos humanos.")
    if {"zs_bug_flag", "zs_divida_tecnica_flag", "zs_feature_request_flag"}.issubset(transformers.columns):
        titulo_secao("Classificação zero-shot")
        zs = pd.DataFrame({"Categoria":["Bug", "Dívida técnica", "Funcionalidade"],
                           "Issues":[int(transformers[c].eq("SIM").sum()) for c in ["zs_bug_flag","zs_divida_tecnica_flag","zs_feature_request_flag"]]})
        grafico_barras(zs,"Categoria","Issues",cor=ROSA,altura=310)
    if avaliacao is not None and not avaliacao.empty:
        titulo_secao("Validação humana")
        mostrar_tabela(avaliacao, list(avaliacao.columns), "Métricas da avaliação")
    mostrar_tabela(transformers, ["repositorio","numero","titulo","sentimento_transformer","confianca_sentimento","zs_bug_flag","zs_divida_tecnica_flag","zs_feature_request_flag"], "Explorar classificações")

st.markdown('<div class="footer">DEVISSUES &nbsp; · &nbsp; OPEN SOURCE INTELLIGENCE &nbsp; · &nbsp; NLP & AI</div>', unsafe_allow_html=True)
