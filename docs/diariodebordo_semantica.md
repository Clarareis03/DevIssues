# Diário de bordo — DevIssues (2ª etapa)

**Integrante:** Ayra Souza
**Data:** 16/11/2026
**Componente:** Trilha A — Pipeline spaCy avançado (`src/pipeline_spacy.py`)

---

## Entrada 1

**Data:** 16/11/2026
**Componente:** Pipeline spaCy
**Problema:** A similaridade entre issues precisa de vetores de palavras, que os modelos `sm` não trazem.

**O que aconteceu:**

Na 1ª etapa o projeto usou os modelos pequenos do spaCy. A trilha A pede similaridade entre issues, e os modelos `sm` não têm vetores de palavras de verdade, então a comparação não teria significado.

**Tentativa de solução:**

Conferimos quais modelos do spaCy trazem vetores e escolhemos a versão média (`md`) de cada idioma.

**Solução encontrada:**

Baixamos os dois modelos com `python -m spacy download en_core_web_md` e `python -m spacy download pt_core_news_md`. Os dois são da versão 3.8.0 (33,5 MB e 42,4 MB) e instalaram sem erro.

**O que aprendemos:**

O tamanho do modelo muda o que dá para fazer: o `sm` serve para etiquetar e reconhecer entidades, mas só o `md` ou o `lg` permitem comparar textos por vetores.

---

## Entrada 2

**Data:** 16/11/2026
**Componente:** Pipeline spaCy
**Problema:** O corpus é bilíngue (210 issues em inglês e 70 em português), mas cada modelo serve a um idioma.

**O que aconteceu:**

Rodar o `en_core_web_md` nas issues do TabNews daria vetores e entidades sem sentido, e comparar uma issue em inglês com uma em português também não faz sentido com um único modelo.

**Tentativa de solução:**

Procuramos no código da etapa 1 alguma forma de separar as issues por idioma.

**Solução encontrada:**

Reaproveitamos `detectar_idioma` e `montar_texto_issue` de `src/nlp.py`. A detecção bateu com o esperado (210 em inglês e 70 em português). O programa agora processa cada grupo com o seu modelo e calcula a similaridade só dentro do mesmo idioma.

**O que aprendemos:**

Uma decisão da coleta (misturar idiomas) se reflete em todas as etapas seguintes. Reaproveitar funções do colega evitou refazer o que já estava resolvido e manteve os resultados comparáveis.

---

## Entrada 3

**Data:** 16/11/2026
**Componente:** Pipeline spaCy
**Problema:** A amostra do protótipo veio toda do mesmo repositório.

**O que aconteceu:**

O protótipo roda em 20 issues em inglês. Como o CSV está ordenado por repositório, as 20 primeiras vieram todas do `psf/requests`, e a tabela de resultados não mostrava nada dos outros dois.

**Tentativa de solução:**

Em vez de pegar as 20 primeiras, passamos a pegar issues de cada repositório.

**Solução encontrada:**

Usamos `groupby("repositorio").head(...)` para montar a amostra. A tabela passou a mostrar issues do `psf/requests`, do `pandas-dev/pandas` e do `microsoft/vscode`.

**O que aprendemos:**

Antes de tirar conclusões de uma amostra pequena, é preciso olhar de onde ela veio. A ordem do arquivo pode esconder um viés.

---

## Entrada 4

**Data:** 16/11/2026
**Componente:** EntityRuler
**Problema:** O padrão de versão marcava números que não eram versões.

**O que aconteceu:**

O primeiro padrão de versão aceitava números com qualquer quantidade de partes. Ele marcou endereços como `169.254.169.254` e `127.0.0.1`. Mesmo limitando a três partes, ainda apareciam números como `5000.0` e `84.9`.

**Tentativa de solução:**

Limitamos o padrão a duas ou três partes. Para os números que sobraram, olhamos o contexto ao redor de cada um.

**Solução encontrada:**

Criamos o componente customizado `filtrar_versoes`, que usa as palavras vizinhas: um número só é versão se começar com `v`, tiver três partes ou vier depois de pistas como `version`, `python` ou o nome de uma biblioteca. Também descarta números seguidos de `%` ou de unidades como `ms`.

**O que aprendemos:**

Um padrão sozinho acha tudo que tem a forma de versão. O contexto é o que separa uma versão de um número qualquer. Foi um bom uso de componente customizado: o filtro entra no pipeline depois do `ner`, como uma etapa nossa.

---

## Entrada 5

**Data:** 16/11/2026
**Componente:** Similaridade
**Problema:** A similaridade ficou muito alta mesmo entre issues de assuntos diferentes.

**O que aconteceu:**

No protótipo, a issue sobre a anotação de tipo de `iter_lines` ficou com similaridade de 0.97 a 0.98 com issues sobre emojis no VS Code e sobre valores escapados em parâmetros, que são assuntos bem diferentes.

**Tentativa de solução:**

Entendemos como o spaCy calcula a similaridade e limitamos o texto usado.

**Solução encontrada:**

O vetor de um texto é a média dos vetores das palavras, então textos longos tendem a se parecer. Para reduzir isso, a similaridade usa só título e início do corpo (até 1500 caracteres) e é calculada dentro de cada idioma. O problema não some totalmente, e vamos mostrar isso como limite no slide de resultados e comparar com os embeddings da Ana Beatriz.

**O que aprendemos:**

Um número alto de similaridade não quer dizer que as issues falam da mesma coisa. Vetores médios ignoram a ordem e o contexto das palavras, e os modelos de frases da trilha B existem para tratar justamente isso.

---

## Entrada 6

**Data:** 16/11/2026
**Componente:** EntityRuler
**Problema:** A palavra `Error` sozinha virava uma entidade de erro.

**O que aconteceu:**

Ao comparar com o Regex da etapa 1, o spaCy marcou `Error` como erro em issues em que o Regex não tinha achado nada. Eram 6 issues nessa situação.

**Tentativa de solução:**

Olhamos o padrão: `^\w*(Error|Exception)$`.

**Solução encontrada:**

O `\w*` aceita zero letras antes de `Error`, então a palavra solta casava. Trocamos por `\w+`, que exige pelo menos uma letra antes. Depois disso, nenhuma issue ficou com erro só do spaCy.

**O que aprendemos:**

O `*` aceita zero ocorrências e o `+` exige pelo menos uma. Uma troca de um caractere mudou o resultado, e só aparece quando comparamos com outro método.

---

## Entrada 7

**Data:** 16/11/2026
**Componente:** EntityRuler e tokenizador
**Problema:** O spaCy deixava passar erros e versões que o Regex da etapa 1 encontrava.

**O que aconteceu:**

Na comparação de erros, o spaCy encontrou os mesmos erros do Regex em 37 issues e deixou passar em 4, além de 1 issue em que os resultados foram diferentes. Exemplos: `SSLError` (psf/requests #7617), `ForbiddenError` (TabNews #1883), `setPasswordMismatchError` (TabNews #1919) e `CodeError` (vscode #338114).

**Tentativa de solução:**

Olhamos como o tokenizador do spaCy quebrou o texto dessas issues. Ele deixa o nome do erro colado na pontuação, gerando tokens como `SSLError(SSLCertVerificationError(1` e `setPasswordMismatchError(true`. O padrão do EntityRuler exige que o token termine em `Error`, então não casava.

**Solução encontrada:**

Criamos a função `ajustar_tokenizador`, que acrescenta regras de separação ao tokenizador do modelo: parênteses, colchetes, chaves, aspas, barra invertida e `=`. Depois disso, o spaCy e o Regex passaram a concordar em todos os erros: 42 issues com os mesmos erros e 238 sem nenhum, sem nenhuma divergência.

Ao olhar as versões que só o Regex achava, vimos o mesmo problema: eram 253 versões de três partes coladas em `|` (tabelas markdown, como `v1.9.0|celery`), em `+` (`6.12.74+deb13`) e em hífen (`2.6.3-py3-none-any`). Acrescentamos `|`, `+` e hífen depois de número às regras do tokenizador. As versões encontradas pelos dois métodos subiram de 530 para 741, e as que só o Regex achava caíram de 296 para 85.

Na comparação também passamos a usar só a parte numérica da versão (`6.8.0-136-generic` vira `6.8.0`), porque o Regex guarda o sufixo e o spaCy não, e o mesmo número aparecia como diferente.

**O que aprendemos:**

Os padrões do EntityRuler trabalham em cima de tokens, não do texto bruto, e em texto técnico (código, tabelas, logs) o tokenizador padrão deixa muita coisa colada. Ajustar o tokenizador foi o que mais melhorou o resultado, mais do que mexer nos padrões. Ainda restam diferenças nas versões: o spaCy acha 166 que o Regex não acha, e o Regex acha 85 que o spaCy não acha. Isso vem de regras diferentes de cada método (o spaCy descarta números de duas partes sem contexto, por exemplo). Sem uma conferência manual, não sabemos qual dos dois acerta mais.

---

## Entrada 8

**Data:** 16/11/2026
**Componente:** EntityRuler
**Problema:** O nome `requests` é ao mesmo tempo biblioteca, nome do repositório e palavra comum.

**O que aconteceu:**

A biblioteca `requests` apareceu em 48 das 70 issues do `psf/requests`, e em só 8 issues dos outros repositórios (1 do TabNews, 5 do VS Code e 2 do pandas). No `psf/requests` ela aparece porque é o assunto do repositório, e em outros lugares pode ser a palavra comum "requests".

**Tentativa de solução:**

Pensamos em usar a classe gramatical da palavra ou o contexto para separar os usos.

**Solução encontrada:**

Ainda em aberto. Por enquanto mantemos o padrão simples e vamos avisar nos slides que a contagem de `requests` no `psf/requests` não diz muito, e que o nome precisa ser conferido nos outros repositórios.

**O que aprendemos:**

Listas de nomes funcionam bem para nomes únicos (`urllib3`, `pyarrow`) e mal para nomes que também são palavras do idioma. Em português e em inglês, nomes comuns exigem checagem do contexto.

---

*Este diário deve continuar sendo atualizado conforme a trilha A avança (versão completa nas 280 issues, comparação com a etapa 1 e integração no dashboard).*
