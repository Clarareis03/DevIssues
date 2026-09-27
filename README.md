# DevIssues

Análise linguística de relatos de problemas em projetos de código aberto: como desenvolvedores descrevem bugs, dívida técnica, pedidos de funcionalidade e urgência nas issues do GitHub.

Projeto desenvolvido para a 1ª etapa da disciplina de Processamento de Linguagem Natural e Engenharia de Software, usando **Expressões Regulares** e **spaCy** sobre um corpus real de **280 issues** coletadas pela GitHub REST API.

> **#6165** — `update docs for MAX_CONTENT_LENGTH`
> "I have this Flask app with... the app kept receiving and writing the request to disk way over 10 bytes..."
> - Bug: NÃO · Feature request: SIM · Urgência: NÃO
>
> **#6139** — `AI junk`
> "Multiple security vulnerabilities in Flask: CRITICAL code execution via exec()..."
> - Bug: SIM · Urgência: SIM · Dívida técnica: NÃO

## Sumário

- [O projeto](#o-projeto)
- [Fonte de dados](#fonte-de-dados)
- [Categorias identificadas](#categorias-identificadas)
- [RE e spaCy](#re-e-spacy)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como rodar](#como-rodar)
- [Resultados](#resultados)
- [Equipe](#equipe)
- [Limitações](#limitações)
- [Diário de bordo](#diário-de-bordo)
- [Próximas etapas](#próximas-etapas)

## O projeto

**Pergunta de pesquisa:** quais padrões linguísticos relacionados a erros, urgência, dívida técnica e pedidos de funcionalidade aparecem nos textos de issues abertas em repositórios de código aberto no GitHub?

**Objetivo geral:** coletar e processar issues públicas do GitHub, utilizando Expressões Regulares e spaCy, para identificar padrões linguísticos associados a bugs, dívida técnica, pedidos de funcionalidade e urgência do relato.

**Objetivos específicos:**

- Coletar issues públicas de repositórios abertos pela API do GitHub e guardá-las em CSV.
- Identificar vocabulário técnico ligado a erros e falhas.
- Identificar sinais de dívida técnica (pedidos de refatoração, código "sujo", workarounds).
- Identificar pedidos de funcionalidade.
- Identificar marcadores explícitos de urgência no relato.
- Classificar a polaridade dos textos (positivo, neutro, negativo).
- Gerar estatísticas e mostrar tudo em uma interface (terminal e dashboard web).

A análise é **exclusivamente textual**: nenhum código-fonte dos repositórios analisados é executado ou avaliado, só título + corpo das issues.

## Fonte de dados

Coleta feita pela **GitHub REST API** (`GET /repos/{owner}/{repo}/issues`), sem scraping, usando um token *fine-grained* com acesso somente leitura a repositórios públicos.

| Repositório | Idioma predominante |
| --- | --- |
| `pallets/flask` | Inglês |
| `psf/requests` | Inglês |
| `pandas-dev/pandas` | Inglês |
| `microsoft/vscode` | Inglês |
| `filipedeschamps/tabnews.com.br` | Português |

**Corpus final: 280 issues** (`dados/issues.csv`), sendo **210 em inglês** e **70 em português** — um corpus bilíngue processado com dois modelos spaCy diferentes (`en_core_web_sm` e `pt_core_news_sm`), escolhidos automaticamente por issue a partir de uma detecção simples de idioma.

## Categorias identificadas

| Categoria | Como é identificada |
| --- | --- |
| **Bug / erro** | Presença de nome de exceção (Regex), labels do GitHub (`bug`, `defect`, `erro`) ou lemas do spaCy (`bug`, `error`, `crash`, `fix`) |
| **Dívida técnica** | Labels (`debt`, `refactor`, `cleanup`, `deprecation`) ou lemas (`refactor`, `deprecated`, `cleanup`) |
| **Pedido de funcionalidade** | Labels (`enhancement`, `feature`, `request`) ou lemas (`feature`, `add`, `support`, `implement`) |
| **Urgência** | Termos explícitos via Regex (`urgent`, `critical`, `asap`, `blocking`, `blocker`, `high priority`) ou labels (`urgent`, `critical`, `p0`, `p1`, `blocker`) |
| **Sentimento** | Positivo, Neutro ou Negativo, a partir da contagem de lemas de satisfação vs. frustração/falha extraídos pelo spaCy |

A comparação de labels e termos é feita por **token exato** (não por substring), para evitar falsos positivos como `"bug"` sendo encontrado dentro de `"debug"`/`"debugging"`.

Uma mesma issue pode pertencer a mais de uma categoria ao mesmo tempo — os números das categorias não somam o total.

## RE e spaCy

### Expressões Regulares (`src/regex.py`)

Aplicadas sobre título + corpo de cada issue para capturar:

- **Versões de software** (ex.: `v3.12.1`, `2.34.2`), com filtros para descartar IPv4, seções de RFC, percentuais, métricas e scores que teriam a mesma estrutura de uma versão;
- **Referências a issues/PRs** (ex.: `#1234`);
- **Erros e exceções** (ex.: `TypeError`, `ValueError`);
- **Caminhos de arquivos** (URLs são mascaradas antes, para não se confundirem com caminhos);
- **URLs**;
- **Termos explícitos de urgência** (`urgent`, `critical`, `asap`, `blocking`, `blocked`, `high priority`, `release blocker`, `blocker`).

### spaCy (`src/nlp.py`)

Para cada issue, na língua detectada:

1. identificação do idioma;
2. tokenização;
3. lematização;
4. remoção de stopwords;
5. identificação de classes gramaticais (POS);
6. extração de entidades nomeadas (NER).

## Estrutura do projeto

```
DevIssues/
│
├── main.py                 # Ponto de entrada (menu no terminal)
├── app.py                  # Dashboard web (Streamlit)
│
├── src/
│   ├── coleta.py            # Coleta via GitHub API
│   ├── regex.py              # Padrões de Expressões Regulares
│   ├── nlp.py                 # Processamento spaCy
│   ├── analise.py             # Classificação, sentimento e consolidação
│   └── interface.py           # Menu interativo do terminal
│
├── dados/
│   └── issues.csv           # 280 issues coletadas
│
├── resultados/
│   ├── regex_results.csv     # Saída bruta do componente Regex
│   ├── nlp_results.csv        # Saída bruta do componente spaCy
│   └── relatorio_final.csv    # Base consolidada e classificada
│
├── docs/
│   ├── diariodebordo_coleta.md
│   ├── diariodebordo_regex_nlp.md
│   └── diariodebordo_analise_interface.md
│
├── requirements.txt
└── README.md
```

## Como rodar

### 1. Pré-requisitos

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download pt_core_news_sm
```

### 2. Configurar o token do GitHub (só necessário para coletar issues novas)

Crie um [Personal Access Token *fine-grained*](https://github.com/settings/personal-access-tokens/new) com **Repository access: Public Repositories (read-only)** e salve num arquivo `.env` na raiz do projeto (não versionado):

```
GITHUB_TOKEN=seu_token_aqui
```

### 3. Rodar a coleta (opcional — o corpus de 280 issues já está em `dados/issues.csv`)

```bash
python -m src.coleta --repos pallets/flask,psf/requests,pandas-dev/pandas,microsoft/vscode,filipedeschamps/tabnews.com.br --max-por-repo 56
```

### 4. Rodar a análise completa

```bash
python -m src.analise
```

Gera `resultados/relatorio_final.csv` e imprime um resumo com o total de issues, bugs, dívida técnica e urgência.

### 5. Usar a interface

Menu no terminal:

```bash
python main.py
```

Dashboard web:

```bash
streamlit run app.py
```

## Resultados

Números reais obtidos ao rodar a análise sobre o corpus completo de 280 issues (ver `resultados/relatorio_final.csv`, `resultados/regex_results.csv` e `resultados/nlp_results.csv` para o detalhamento issue a issue).

**Classificação (`src/analise.py`):**

| Categoria | Quantidade |
| --- | --- |
| Total de issues analisadas | 280 |
| Bugs / erros | 147 |
| Dívida técnica | 35 |
| Urgência | 6 (2,1%) |

**Padrões Regex (`src/regex.py`), % das 280 issues em que o padrão foi encontrado:**

| Padrão | Issues | % |
| --- | --- | --- |
| Versões | 106 | 37,9% |
| URLs | 154 | 55,0% |
| Caminhos de arquivos | 48 | 17,1% |
| Referências (#123) | 45 | 16,1% |
| Erros/exceções | 42 | 15,0% |
| Urgência | 6 | 2,1% |

**Processamento spaCy (`src/nlp.py`):**

- 210 issues em inglês, 70 em português;
- 101.509 tokens processados;
- 5.705 entidades nomeadas extraídas.

> A contagem de urgência foi recalculada durante a integração da base completa (o valor de 4 issues / 1,4%, que aparece em versões anteriores do diário de bordo, refletia um corpus ainda incompleto). O número correto, confirmado sobre as 280 issues, é **6 issues (2,1%)**.

Para categorias e recortes adicionais (feature request, distribuição de sentimento, top erros e versões mais citados), consulte diretamente `resultados/relatorio_final.csv` ou o dashboard em `app.py`.

## Equipe

| Responsabilidade | Integrante | Arquivos |
| --- | --- | --- |
| Coleta de dados (GitHub API) | Ayra Souza | `src/coleta.py`, `dados/issues.csv` |
| Regex e spaCy | Ana Beatriz | `src/regex.py`, `src/nlp.py` |
| Análise, interface e dashboard | Maria Clara Reis | `src/analise.py`, `src/interface.py`, `app.py`, `main.py` |

## Limitações

1. O projeto analisa **textos de issues**, não a qualidade real do código nem o desempenho dos desenvolvedores.
2. A análise de sentimento é automática e baseada em lista de lemas — pode errar, especialmente com sarcasmo ou gírias técnicas.
3. Encontrar termos como "urgent" ou "critical" não significa que o problema era, de fato, grave — pode ser só o jeito de quem escreveu.
4. A amostra depende dos cinco repositórios escolhidos, que têm culturas de comunicação diferentes (inclusive volume relevante de spam/conteúdo gerado por IA em alguns deles, como no `pallets/flask`).
5. Não devemos generalizar os resultados para todo o ecossistema open source.
6. A detecção de idioma usa uma heurística simples baseada em listas de palavras-chave; casos ambíguos são classificados por padrão como inglês.
7. A 1ª etapa é exclusivamente textual.

## Diário de bordo

Cada integrante documentou problemas encontrados e soluções em tempo real:

- [`docs/diariodebordo_coleta.md`](docs/diariodebordo_coleta.md) — configuração de token, troca de repositório (`frontendbr/open-source` → `filipedeschamps/tabnews.com.br`), consolidação do corpus bilíngue.
- [`docs/diariodebordo_regex_nlp.md`](docs/diariodebordo_regex_nlp.md) — refinamento dos padrões Regex (falsos positivos de versão, sobreposição caminho/URL) e configuração do spaCy para os dois idiomas.
- [`docs/diariodebordo_analise_interface.md`](docs/diariodebordo_analise_interface.md) — normalização de lemas para o sentimento e migração da interface de terminal para o dashboard em Streamlit.

## Próximas etapas

O tema é o mesmo nas três etapas da disciplina; muda o tipo de dado analisado:

```
1ª ETAPA — TEXTO       → RE + spaCy + GitHub API      (concluída)
2ª ETAPA — ÁUDIO        → módulos Python para áudio
3ª ETAPA — VÍDEO         → módulos Python para vídeo
```