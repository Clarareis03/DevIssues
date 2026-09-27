Plano de execução da 1ª etapa

# DevIssues

Análise linguística de relatos de problemas em projetos de código aberto: como desenvolvedores descrevem bugs, dívida técnica, pedidos de funcionalidade e urgência nas issues do GitHub.

#128 — Critical: app crashes on login since v2.3.1

“Getting a NullPointerException every time. This is blocking our release, please fix ASAP.”

- **Bug:** SIM
- **Urgência:** SIM
- **Dívida técnica:** NÃO

#204 — Feature request: add dark mode support

“Would be nice to have a dark theme option. Also this component could use a refactor, it's getting messy.”

- **Feature request:** SIM
- **Dívida técnica:** SIM
- **Bug:** NÃO

bug / erro dívida técnica pedido de funcionalidade urgência

[Resumo](#resumo) [Regras da professora](#regras) [O projeto](#projeto) [O que faz](#funcoes) [RE e spaCy](#tecnologias) [Coleta de dados](#coleta) [Categorias](#categorias) [Estrutura](#estrutura) [Fluxo](#fluxo) [Quem faz o quê](#divisao) [Cronograma](#cronograma) [Diário de bordo](#diario) [Slides](#slides) [Resultados](#resultados) [Limitações](#limites) [Próximas etapas](#proximas) [Checklist](#checklist) [Decidir hoje](#decidir)

## Resumo rápido

Chegou agora no grupo? Leia esta parte, depois "Quem faz o quê" e o checklist. O resto é para consultar quando precisar.

O que vamos fazer

Um programa em Python que coleta issues públicas do GitHub e marca nelas sinais de bug, dívida técnica, pedido de funcionalidade, urgência e polaridade textual (positivo, neutro, negativo).

Por que

A 1ª etapa da disciplina pede PLN com Expressões Regulares e spaCy, mais coleta via BeautifulSoup, rede social/GitHub ou Web API. O GitHub é citado diretamente como fonte permitida, e sua API é pública e bem documentada.

Como

Coleta pela API do GitHub, limpeza, Regex, spaCy, classificação por categorias, estatísticas e um menu simples para mostrar tudo funcionando.

Quem

Três integrantes: uma na coleta, uma no núcleo de PLN (Regex e spaCy) e uma na análise, interface e apresentação.

Como marcamos o que ainda não está decidido

Tudo o que aparece como a definir pela equipe é decisão nossa. Nada aqui foi inventado como resultado, repositório ou número real já confirmado.

## O que a professora pediu

### As três etapas

| Etapa | O que precisa ter |
| --- | --- |
| **1ª** | PLN com **RE (Expressões Regulares)** e **spaCy**. Coleta com **BeautifulSoup** (web scraping) *ou* dados de rede social (ex.: Twitter, GitHub) *ou* Web API. |
| **2ª** | Análise de áudio com módulos Python. |
| **3ª** | Análise de vídeo com módulos Python. |

Prazo do tema

O tema de cada etapa precisa ser informado no **grupo de WhatsApp da disciplina até dois dias antes da apresentação**. Na 1ª etapa, atrasar diminui a nota.

### Regras de código

- Pelo menos **50 linhas de código por componente**.
- Se usarmos tecnologia ou framework que **não foi apresentado em sala**, esse mínimo pode cair para **30 linhas**, salvo exceções combinadas com a professora.
- Precisamos usar os assuntos trabalhados em aula que correspondem a cada etapa.

### Como a apresentação deve ser

Com editor de slides, mais ou menos nesta sequência:

1. Explicação inicial do tema.
2. Fórmulas ou teorias usadas e seus parâmetros.
3. Como a teoria foi implementada no programa.
4. Explicação dos comandos usados.
5. Se houver biblioteca nova, dicas de onde aprender.
6. Erros encontrados e como resolvemos, por meio do diário de bordo.
7. Programa funcionando com todas as opções.

## O projeto

### Tema

**Análise linguística de relatos de problemas em projetos de código aberto.**

Por que esse tema é Engenharia de Software

O assunto analisado é o próprio processo de desenvolver software: como devs relatam bugs, pedem funcionalidades, sinalizam dívida técnica e comunicam urgência. Diferente de um projeto que só usa Python como ferramenta, aqui o **tema em si** é sobre engenharia de software.

Pergunta de pesquisa

> Quais padrões linguísticos relacionados a erros, urgência, dívida técnica e pedidos de funcionalidade aparecem nos textos de issues abertas em repositórios de código aberto no GitHub?

Objetivo geral

Desenvolver uma aplicação capaz de coletar e processar issues públicas do GitHub, utilizando Expressões Regulares e spaCy para identificar padrões linguísticos associados a bugs, dívida técnica, pedidos de funcionalidade e urgência do relato.

### Objetivos específicos

- Coletar issues públicas de repositórios abertos pela API do GitHub e guardá-las em CSV.
- Identificar vocabulário técnico ligado a erros e falhas.
- Identificar sinais de dívida técnica (pedidos de refatoração, código "sujo", workarounds).
- Identificar pedidos de funcionalidade.
- Identificar marcadores de urgência no relato.
- Classificar a polaridade dos textos de forma simples.
- Gerar estatísticas e mostrar tudo em uma interface simples.

## O que o DevIssues vai fazer

A 1ª etapa é **exclusivamente textual**. O sistema trabalha com issues públicas do GitHub e tenta identificar, quando possível:

| O que identifica | Exemplos de termos e expressões |
| --- | --- |
| **Bug / erro** | error, exception, crash, fails, bug, traceback, stack trace, broken |
| **Dívida técnica** | refactor, technical debt, cleanup, deprecated, workaround, hack, messy code |
| **Pedido de funcionalidade** | feature request, enhancement, "would be nice", "please add", "could we have" |
| **Urgência** | urgent, critical, blocking, ASAP, "breaks production", high priority |
| **Sentimento textual** | positivo, neutro ou negativo |

Sobre o sentimento

É uma **classificação automática do texto**. Ela não mede a frustração real de quem escreveu, só palavras que costumam indicar tom positivo ou negativo.

Detalhe técnico: se as issues coletadas forem em inglês (o mais comum em projetos open source grandes), o modelo do spaCy usado deve ser o de inglês (`en_core_web_sm`), não o de português. Isso deve ficar decidido junto com a fonte de dados.

## Onde entram RE e spaCy

### RE (Expressões Regulares)

Servem para achar **padrões de escrita** no texto. Vamos usar para:

- números de versão (ex.: v2.3.1);
- referências a outras issues ou pull requests (ex.: #123);
- nomes de erros e exceções (ex.: TypeError, NullPointerException);
- caminhos de arquivo e trechos de código;
- links de commits ou PRs.

Exemplo do padrão para número de versão:

```
padrao_versao = r'\bv?\d+\.\d+(?:\.\d+)?\b'
```

Testamos esse padrão e ele encontra corretamente `v2.3.1`, `2.10.0` e `1.0`, sem confundir com números soltos no texto.

Exemplo do padrão para referência a issue/PR:

```
padrao_referencia = r'#\d+'
```

Acha coisas como `#123` em frases do tipo "Closes #123" ou "relacionado a #45".

Exemplo do padrão para nomes de erro:

```
padrao_erro = r'\b\w*Error\b|\b\w*Exception\b'
```

Encontra `TypeError`, `ValueError`, `NullPointerException` e variações, mesmo com prefixos diferentes.

### spaCy

Biblioteca de PLN que "entende" a estrutura da frase. Vamos usar para:

- tokenização (quebrar o texto em palavras);
- lematização (levar "crashing" e "crashed" para a forma base "crash");
- stopwords (palavras muito comuns, como "the" e "a");
- classes gramaticais (verbo, substantivo etc.);
- entidades (nomes de tecnologias, números de versão, organizações);
- processamento linguístico geral dos textos.

```
import spacy

nlp = spacy.load("en_core_web_sm")

doc = nlp("The app crashes every time I click login.")

for token in doc:
    print(token.text, token.pos_)
```

**O que esse código faz, em português simples:**

1. `import spacy` traz a biblioteca.
2. `spacy.load(...)` carrega o modelo de inglês (pequeno). Ele precisa ser baixado antes, com `python -m spacy download en_core_web_sm`.
3. `nlp("...")` processa a frase e devolve um `doc`, já dividido em tokens.
4. O `for` passa por cada token e imprime a palavra (`token.text`) e sua classe gramatical (`token.pos_`), por exemplo verbo ou substantivo.

Se as issues escolhidas forem em português

Existem repositórios open source brasileiros com issues em português (ex.: projetos de comunidades locais). Nesse caso, trocamos para `pt_core_news_sm`, igual ao exemplo acima faria em inglês. Essa escolha depende da fonte de dados, que ainda é a definir pela equipe.

### Estamos usando algo que a professora não apresentou?

Precisamos conferir isso para saber se vale a regra de 30 linhas. Esta tabela é para a equipe preencher.

| Tecnologia | Para que | Situação |
| --- | --- | --- |
| Expressões Regulares (`re`) | Padrões no texto | Exigida pela professora |
| spaCy | Núcleo de PLN | Exigida pela professora |
| Biblioteca de requisições (ex.: `requests`) | Consumir a API do GitHub | a conferir |
| CSV (`csv` ou pandas) | Guardar e ler issues | a conferir |
| Gráficos (ex.: matplotlib), se usarmos | Mostrar estatísticas | a conferir |
| Biblioteca de interface gráfica, se usarmos | Interface | a conferir. Menu no terminal não precisa de nada extra |

## Coleta dos dados

A fonte escolhida é a **GitHub REST API**, que está explicitamente entre as fontes permitidas pela professora. A estratégia é:

**coleta automatizada, depois armazenamento das issues, depois processamento.** As issues ficam em `dados/issues.csv`.

Por que a API do GitHub é uma boa escolha

É pública, bem documentada e não exige login para ler repositórios abertos — só um token pessoal gratuito, recomendado para não esbarrar no limite de requisições sem autenticação. Isso evita as limitações de acesso que redes como Instagram, TikTok ou X/Twitter costumam ter.

| O que coletar | Campo da API | Uso no projeto |
| --- | --- | --- |
| Título da issue | `title` | Texto principal a ser analisado |
| Corpo da issue | `body` | Texto principal a ser analisado |
| Rótulos (labels) | `labels` | Comparar com a classificação automática do programa |
| Data de criação | `created_at` | Contexto, não obrigatório na 1ª etapa |
| Repositório de origem | — | Registrar de qual repositório veio cada issue |

**Nenhum repositório está confirmado ainda.** Sugestão de critério para escolher: repositórios open source ativos, com bastante gente relatando bugs e pedindo funcionalidades, e de preferência numa linguagem que o grupo conheça. A escolha final é decisão das três.

### Quantidade de issues

Começar com algo entre **100 e 500 issues**, de 2 a 3 repositórios. Se a coleta funcionar bem, a quantidade cresce.

## Classificação por categorias

A primeira abordagem é **baseada em vocabulário e padrões**: cada categoria tem uma lista de termos, e o programa vê se o texto contém algum deles.

```
categorias = {
    "bug": [
        "error", "exception", "crash", "fails", "bug", "broken"
    ],

    "divida_tecnica": [
        "refactor", "technical debt", "cleanup", "deprecated", "workaround"
    ],

    "feature_request": [
        "feature request", "enhancement", "would be nice", "please add"
    ],

    "urgencia": [
        "urgent", "critical", "blocking", "asap", "high priority"
    ]
}
```

### Exemplos do resultado esperado

| Texto (título + corpo) | Bug | Urgência | Dívida técnica |
| --- | --- | --- | --- |
| "Critical: app crashes on login. Getting a NullPointerException, blocking our release." | SIM | SIM | NÃO |
| "Feature request: add dark mode. Also this component could use a refactor." | NÃO | NÃO | SIM |

Dois pontos para a equipe pensar

- **Rótulos (labels) do próprio GitHub podem ajudar a validar.** Muitos repositórios já marcam issues com labels como "bug" ou "enhancement". Dá pra comparar a classificação automática do programa com esses rótulos, como uma checagem extra — sem usar o rótulo como resposta certa absoluta, porque as pessoas nem sempre marcam direito.
- **Uma issue pode ter mais de uma categoria ao mesmo tempo**, como no exemplo 2 acima (feature request e dívida técnica juntos). Isso é esperado e não precisa ser "corrigido".

## Estrutura do projeto

```
DevIssues/
│
├── main.py
│
├── src/
│   ├── coleta.py
│   ├── regex.py
│   ├── nlp.py
│   ├── analise.py
│   └── interface.py
│
├── dados/
│   └── issues.csv
│
├── resultados/
│
├── requirements.txt
│
└── README.md
```

| Arquivo | Função | Quem |
| --- | --- | --- |
| `main.py` | Ponto de entrada: liga os módulos e inicia o programa. | Pessoa 3 |
| `src/coleta.py` | Busca issues na API do GitHub e salva em CSV. | Pessoa 1 |
| `src/regex.py` | Padrões de Expressões Regulares: versões, referências, nomes de erro. | Pessoa 2 |
| `src/nlp.py` | Tudo do spaCy: tokenização, lematização, stopwords, classes gramaticais, entidades. | Pessoa 2 |
| `src/analise.py` | Junta os resultados, classifica, analisa sentimento e gera estatísticas. | Pessoa 3 |
| `src/interface.py` | Menu e exibição dos resultados. | Pessoa 3 |
| `dados/issues.csv` | Issues coletadas. | Pessoa 1 gera |
| `resultados/` | Saídas do programa (estatísticas, listas de issues classificadas). | Pessoa 3 |
| `requirements.txt` | Bibliotecas do projeto, para qualquer uma instalar igual. | Todas |
| `README.md` | Como instalar e rodar. | Todas |

Sobre as 50 linhas por componente

Por isso não fazemos um arquivo gigante: cada módulo tem uma responsabilidade clara e código de verdade, com pelo menos 50 linhas (ou 30, se a regra da tecnologia nova valer). Vale checar o número de linhas de cada arquivo antes da apresentação.

## Fluxo completo do programa

```
COLETA DE ISSUES (GitHub API)
       ↓
LIMPEZA DOS TEXTOS
       ↓
REGEX
       ↓
SPACY
       ↓
IDENTIFICAÇÃO DE PADRÕES
       ↓
CLASSIFICAÇÃO
       ↓
ANÁLISE
       ↓
RESULTADOS
```

1. Coleta de issues

   `coleta.py` busca issues pela API do GitHub e salva em `dados/issues.csv`.
2. Limpeza dos textos

   Tira formatação Markdown, blocos de código muito longos, espaços extras e duplicados.
3. Regex

   Acha números de versão, referências a issues/PRs e nomes de erros e exceções.
4. spaCy

   Divide em tokens, leva palavras à forma base, tira stopwords e marca classes gramaticais e entidades.
5. Identificação de padrões

   Reúne, por issue, o que Regex e spaCy encontraram.
6. Classificação

   Aplica as categorias (bug, dívida técnica, feature request, urgência) e a polaridade.
7. Análise

   Conta, calcula porcentagens e compara com os rótulos originais do GitHub.
8. Resultados

   Mostra no menu do programa e guarda em `resultados/`.

### Interface: ponto de partida

Pode começar simples, um menu no terminal:

```
==================================
          DEVISSUES
==================================

1 - Coletar issues
2 - Processar textos
3 - Detectar bugs
4 - Detectar dívida técnica
5 - Detectar pedidos de funcionalidade
6 - Analisar urgência e sentimento
7 - Mostrar estatísticas
8 - Sair

Digite uma opção:
```

## Quem faz o quê

A divisão é equilibrada entre as três. Os nomes de cada uma ficam a definir pela equipe.

1

### Coleta de dados

Integrante: a definir

#### Arquivo principal

`src/coleta.py` gera `dados/issues.csv`

#### Responsabilidades

- Escolher os repositórios junto com a equipe.
- Implementar a consulta à GitHub REST API.
- Coletar título, corpo e labels das issues.
- Limpar formatação Markdown e remover informações desnecessárias.
- Salvar em CSV.
- Testar a quantidade de dados e os limites de requisição da API.
- Documentar problemas de coleta no diário de bordo.

**Na apresentação (sugestão):** repositórios escolhidos, como a API funciona e dicas de onde aprender a usá-la.

2

### PLN, Regex e spaCy

Integrante: a definir

#### Arquivos

`src/regex.py` e `src/nlp.py`

#### Responsabilidades

- Limpeza textual.
- Tokenização, lematização, stopwords, classes gramaticais e entidades.
- Expressões regulares.
- Identificar termos de bug, dívida técnica, feature request e urgência.
- Preparar os textos para a análise.

**Na apresentação:** explica a teoria de RE e de spaCy, mostra os padrões e o código, e dá dicas de onde aprender.

3

### Análise, interface e apresentação

Integrante: a definir

#### Arquivos

`src/analise.py` e `src/interface.py` (e o `main.py`, que integra tudo)

#### Responsabilidades

- Integrar os dados processados.
- Gerar estatísticas e contar categorias.
- Analisar sentimento.
- Apresentar os resultados e criar a interface simples.
- Integrar os módulos.
- Ajudar na montagem dos slides e organizar o diário de bordo.
- Preparar a demonstração final.

**Na apresentação (sugestão):** resultados, diário de bordo e programa funcionando.

## Cronograma

Modelo de 7 dias. **Se o prazo real for diferente, a gente ajusta**. O que não pode mudar: informar o tema no WhatsApp até dois dias antes da apresentação.

### Dia 1Definição

Todas

- Fechar tema, pergunta de pesquisa e objetivo.
- Escolher os repositórios e definir categorias.
- Informar o tema no WhatsApp da disciplina, dentro do prazo.

### Dia 2Coleta

Pessoa 1: implementar a coleta via GitHub API, testar limites de requisição e salvar as primeiras issues.

Pessoa 2: começar os padrões Regex.

Pessoa 3: começar a estrutura da interface e a documentação.

### Dia 3Regex

Pessoa 2: versões, referências a issues/PRs, nomes de erro, urgência.

### Dia 4spaCy

Pessoa 2: tokenização, lematização, stopwords, classes gramaticais e entidades.

### Dia 5Análise

Pessoa 3: integração, classificação, estatísticas e comparação com os labels do GitHub.

### Dia 6Interface e testes

Todas

- Integração final, testes e correção de erros.
- Programa funcionando com todas as opções do menu.

### Dia 7Apresentação

Todas

- Slides e diário de bordo.
- Ensaio e demonstração.

*Enquanto uma parte espera outra, dá para testar com poucas issues copiadas à mão em `dados/issues.csv`. Assim ninguém fica parada.*

## Diário de bordo

A professora quer ver os erros que encontramos e como resolvemos. Então a regra é: **registrar desde o primeiro dia**, na hora em que o problema aparece.

```
DIÁRIO DE BORDO — DEVISSUES

Data:
Integrante:
Componente:
Problema:
O que aconteceu:
Tentativa de solução:
Solução encontrada:
O que aprendemos:
```

Atenção: os exemplos abaixo são hipotéticos

São problemas que **podem acontecer** durante o projeto. **Nenhum deles aconteceu ainda.** Só entram no diário de verdade se e quando ocorrerem.

| Problema possível | Possível causa | Tentativa | Possível solução |
| --- | --- | --- | --- |
| API do GitHub retornou erro 403 durante a coleta. | Limite de requisições sem autenticação foi excedido. | Repetir a requisição depois de um tempo. | Usar um token pessoal de acesso para aumentar o limite. |
| Regex não identificou determinado nome de erro. | Padrão não previa aquela variação de nome. | Testar o padrão com issues reais. | Revisar e ampliar o padrão da expressão regular. |

## Estrutura dos slides

Segue a sequência pedida pela professora. A coluna "Quem" é só sugestão.

1. Capa

   DevIssues. *Todas.*
2. Tema e problema

   O que queremos investigar: como devs relatam problemas em código aberto. *Todas.*
3. Objetivo

   Objetivo geral e objetivos específicos. *Todas.*
4. Fonte dos dados

   Repositórios escolhidos e a GitHub API. *Pessoa 1.*
5. Metodologia

   O fluxo completo, da coleta aos resultados. *Todas.*
6. Expressões Regulares

   Teoria e exemplos (versão, referência, nomes de erro). *Pessoa 2.*
7. spaCy

   Teoria e exemplo de código. *Pessoa 2.*
8. Arquitetura do sistema

   Os módulos e o que cada um faz. *Pessoa 3.*
9. Implementação

   Trechos importantes do código, explicando os comandos. *Cada uma o seu módulo.*
10. Resultados

    Estatísticas e exemplos reais, comparados com os labels do GitHub. *Pessoa 3.*
11. Diário de bordo

    Erros encontrados e soluções. *Todas.*
12. Programa funcionando

    Demonstração ao vivo com todas as opções do menu. *Pessoa 3, com apoio.*
13. Conclusão

    O que conseguimos fazer e as limitações. *Todas.*
14. Referências

    Documentação da GitHub API, do módulo `re` e do spaCy.

## Como os resultados podem aparecer

Estes números são apenas um exemplo de formato

**Não são resultados reais** e não devem ser citados como tal. Só valem os números que o programa gerar depois de rodar com as issues coletadas.

```
[EXEMPLO DE FORMATO — NÃO SÃO DADOS REAIS]

Total de issues: 400

Issues classificadas como bug: 150
Issues com sinais de dívida técnica: 60
Issues classificadas como feature request: 110
Issues marcadas como urgentes: 45

Sentimento:
Positivo: 15%
Neutro: 55%
Negativo: 30%
```

Uma mesma issue pode ter mais de uma categoria (o exemplo do slide de capa é bug *e* urgente ao mesmo tempo). Por isso os números das categorias não precisam somar o total.

## Limitações e cuidados

Isso deve aparecer na apresentação também, na conclusão.

1. **O projeto analisa textos de issues, não a qualidade real do código** nem o desempenho dos desenvolvedores.
2. **A análise de sentimento é automática** e pode errar, especialmente com sarcasmo ou gírias técnicas.
3. Encontrar a palavra "urgent" ou "critical" **não significa que o problema era, de fato, grave** — pode ser só o jeito de quem escreveu.
4. A amostra depende dos repositórios escolhidos, que podem ter uma cultura de comunicação diferente de outros projetos.
5. Não devemos generalizar os resultados para todo o ecossistema open source.
6. A coleta deve **respeitar os limites de uso da API do GitHub** (rate limits e termos de uso).
7. Não coletar dados pessoais desnecessários (e-mails, nomes completos fora do necessário).
8. A 1ª etapa é **exclusivamente textual**.

## Como o projeto continua

O tema é o mesmo nas três etapas. O que muda é o tipo de dado, e o DevIssues vai ganhando novas modalidades.

```
1ª ETAPA
TEXTO
RE + spaCy + GitHub API
        ↓
DevIssues

2ª ETAPA
ÁUDIO
Módulos Python para análise de áudio
        ↓
DevIssues

3ª ETAPA
VÍDEO
Módulos Python para análise de vídeo
        ↓
DevIssues
```

Cada etapa também exige informar o tema no WhatsApp até dois dias antes da apresentação. Um caminho possível para as próximas etapas: análise de áudio de daily meetings ou de vídeos de code review — mas isso é conversa para mais adiante.

## Próximos passos imediatos

0 de 17

As marcações ficam só neste aparelho. Cada uma marca a sua.

### Combinar

- [ ] Confirmar as três integrantes
- [ ] Confirmar o nome do projeto
- [ ] Informar o tema no WhatsApp da disciplina
- [ ] Escolher os repositórios do GitHub
- [ ] Definir quantidade inicial de issues

### Montar

- [ ] Criar repositório/pasta do projeto
- [ ] Criar estrutura de pastas
- [ ] Criar componente de coleta (GitHub API)
- [ ] Criar componente Regex
- [ ] Criar componente spaCy
- [ ] Criar componente de análise
- [ ] Criar interface

### Testar e apresentar

- [ ] Registrar erros no diário de bordo
- [ ] Fazer testes
- [ ] Conferir requisito de 50 linhas por componente
- [ ] Montar slides
- [ ] Ensaiar apresentação

## O que precisamos decidir juntas hoje

Sete decisões. A coluna do meio é só uma sugestão para começar a conversa.

| Decisão | Sugestão inicial | Decidimos |
| --- | --- | --- |
| **1. Repositórios do GitHub** | 2 a 3 repositórios open source ativos, de preferência numa linguagem que o grupo conheça. | a definir pela equipe |
| **2. Quantidade inicial de issues** | Entre 100 e 500, crescendo se a coleta funcionar. | a definir pela equipe |
| **3. Divisão definitiva das tarefas** | Pessoa 1 coleta, Pessoa 2 Regex e spaCy, Pessoa 3 análise, interface e apresentação. Falta dizer quem é quem. | a definir pela equipe |
| **4. Prazo interno** | Usar o cronograma de 7 dias e encaixar na data real da apresentação. Contar o prazo de dois dias antes para informar o tema. | a definir pela equipe |
| **5. Forma da interface** | Menu no terminal primeiro. Interface gráfica só se sobrar tempo. | a definir pela equipe |
| **6. Idioma das issues (e modelo do spaCy)** | Inglês (modelo `en_core_web_sm`) se os repositórios forem internacionais; português (`pt_core_news_sm`) se forem de comunidades brasileiras. | a definir pela equipe |
| **7. Nome definitivo do projeto** | DevIssues, com o subtítulo sobre relatos de problemas em código aberto. | a definir pela equipe |

Plano de execução da 1ª etapa. Ainda não há dados coletados nem resultados reais: tudo aqui é planejamento.