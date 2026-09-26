# Diário de bordo — DevIssues

**Integrante:** Ana Beatriz
**Data:** 26/09/2026
**Componente:** Processamento textual — Regex e PLN com spaCy

---

## Entrada 1

**Data:** dia 2 do desenvolvimento
**Componente:** Regex
**Problema:** Definição dos padrões Regex que seriam utilizados na análise das issues.

**O que aconteceu:**

Precisávamos definir quais informações técnicas poderiam ser identificadas diretamente no texto das issues utilizando expressões regulares. O projeto previa a identificação de versões, referências de issues/PRs, nomes de erros e exceções, caminhos de arquivos, URLs e termos relacionados à urgência.

**Tentativa de solução:**

Começamos utilizando padrões mais gerais para localizar essas informações no corpus real de 280 issues coletadas pela equipe. Depois da primeira execução, analisamos os resultados para verificar se os padrões estavam realmente encontrando as informações esperadas.

**Solução encontrada:**

Foram definidos padrões específicos para cada tipo de informação, como versões numéricas, referências no formato `#123`, nomes terminados em `Error` ou `Exception`, caminhos de arquivos, URLs e termos explícitos de urgência.

**O que aprendemos:**

Uma expressão regular muito genérica pode encontrar muitos resultados, mas isso não significa que todos sejam relevantes. No processamento de textos técnicos, é necessário analisar os resultados reais e ajustar os padrões de acordo com o contexto em que aparecem.

---

## Entrada 2

**Data:** dia 2 do desenvolvimento
**Componente:** Regex
**Problema:** Falsos positivos na identificação de versões.

**O que aconteceu:**

O primeiro padrão utilizado para encontrar versões identificava muitos números que não representavam versões de software. Foram encontrados casos como endereços IP, percentuais, métricas e outros números decimais presentes nas issues.

**Tentativa de solução:**

Analisamos exemplos reais dos resultados e identificamos quais tipos de números estavam sendo confundidos com versões. A partir disso, foram criados filtros complementares para remover padrões que não representavam versões.

**Solução encontrada:**

O padrão de versões foi refinado e passou a considerar o contexto do número. Também foram adicionados filtros para ignorar endereços IP, referências a seções de RFC, percentuais, métricas e outros valores numéricos que não apresentavam contexto de versão.

**O que aprendemos:**

Em dados reais, identificar um padrão apenas pela sua estrutura pode gerar muitos falsos positivos. O contexto textual é importante para diferenciar uma versão como `2.34.2` de outros números que possuem estrutura semelhante, mas representam outra informação.

---

## Entrada 3

**Data:** dia 2 do desenvolvimento
**Componente:** Regex
**Problema:** Caminhos de arquivos sendo confundidos com partes de URLs.

**O que aconteceu:**

Ao utilizar um padrão para identificar caminhos de arquivos, alguns trechos de URLs também eram reconhecidos como possíveis caminhos. Isso aumentava artificialmente a quantidade de ocorrências encontradas.

**Tentativa de solução:**

Comparamos os resultados encontrados pelo Regex de caminhos com as URLs identificadas no mesmo texto e percebemos que os dois padrões estavam sobrepostos em alguns casos.

**Solução encontrada:**

Antes da identificação dos caminhos de arquivos, as URLs passaram a ser mascaradas temporariamente no texto. Dessa forma, o Regex responsável pelos caminhos não analisava os trechos que já haviam sido identificados como URLs.

**O que aprendemos:**

Quando diferentes padrões Regex procuram estruturas parecidas, a ordem de processamento pode influenciar o resultado. Uma estratégia importante é tratar primeiro os padrões mais específicos ou criar etapas de exclusão para evitar sobreposição entre categorias.

---

## Entrada 4

**Data:** dia 2 do desenvolvimento
**Componente:** Regex
**Problema:** Necessidade de identificar urgência nas issues sem considerar qualquer palavra relacionada a problemas como urgência.

**O que aconteceu:**

O projeto precisava identificar sinais explícitos de urgência nos relatos. Entretanto, termos relacionados a problemas ou bugs não necessariamente indicam que uma issue seja urgente.

**Tentativa de solução:**

Foram analisados os textos das issues procurando termos que indicassem explicitamente prioridade ou bloqueio, em vez de utilizar todos os termos relacionados a bugs.

**Solução encontrada:**

Foi criado um padrão específico para termos como `urgent`, `urgently`, `critical`, `asap`, `blocking`, `blocked`, `high priority`, `release blocker` e `blocker`.

Após a execução sobre as 280 issues, foram encontradas **4 issues com indicação explícita de urgência**, correspondendo a **1,4% do corpus**.

**O que aprendemos:**

É importante diferenciar a existência de um problema da prioridade atribuída a ele. Uma issue pode descrever um bug sem necessariamente indicar urgência. Por isso, a análise utilizou termos explícitos de prioridade e bloqueio.

---

## Entrada 5

**Data:** dia 3 do desenvolvimento
**Componente:** Regex
**Problema:** Validação dos resultados dos padrões sobre o corpus completo.

**O que aconteceu:**

Depois dos refinamentos, foi necessário executar novamente a análise sobre as 280 issues e verificar se os resultados estavam coerentes.

**Tentativa de solução:**

Executamos o script completo e analisamos a quantidade de issues em que cada padrão foi encontrado.

**Solução encontrada:**

A versão final da análise apresentou os seguintes resultados:

* **Versões:** 106 issues (37,9%)
* **Referências:** 45 issues (16,1%)
* **Erros/exceções:** 42 issues (15,0%)
* **Caminhos de arquivos:** 48 issues (17,1%)
* **URLs:** 154 issues (55,0%)
* **Urgência:** 4 issues (1,4%)

O resultado foi salvo em `resultados/regex_results.csv`.

**O que aprendemos:**

A validação com o corpus completo é importante porque uma expressão regular pode funcionar corretamente em alguns exemplos isolados e apresentar problemas quando aplicada a centenas de textos diferentes. Também aprendemos a utilizar os resultados quantitativos para verificar o comportamento dos padrões.

---

## Entrada 6

**Data:** dia 3 do desenvolvimento
**Componente:** PLN com spaCy
**Problema:** Configuração do ambiente para utilização do spaCy.

**O que aconteceu:**

Ao tentar instalar e executar os modelos do spaCy no macOS, o comando `python` não estava disponível no terminal. Depois, ao utilizar `python3`, identificamos que o spaCy ainda não estava instalado no ambiente utilizado.

**Tentativa de solução:**

Primeiro, substituímos o comando `python` por `python3`. Em seguida, instalamos o spaCy no ambiente Python utilizado pelo projeto.

**Solução encontrada:**

O spaCy foi instalado corretamente e a versão utilizada no ambiente passou a ser a **3.8.16**. Depois disso, os modelos necessários para os dois idiomas do corpus foram instalados.

**O que aprendemos:**

A execução de comandos Python pode variar de acordo com o sistema operacional e a configuração do ambiente. Também aprendemos a verificar se uma biblioteca está instalada no mesmo interpretador Python utilizado para executar o projeto.

---

## Entrada 7

**Data:** dia 4 do desenvolvimento
**Componente:** PLN com spaCy
**Problema:** O corpus possuía issues em inglês e português.

**O que aconteceu:**

Ao processar os dados coletados, identificamos que o corpus possuía dois idiomas. As issues dos repositórios `psf/requests`, `pandas-dev/pandas` e `microsoft/vscode` estavam predominantemente em inglês, enquanto o repositório `filipedeschamps/tabnews.com.br` fornecia issues em português.

Como o spaCy utiliza modelos específicos para cada idioma, não seria adequado aplicar o mesmo modelo a todas as issues.

**Tentativa de solução:**

Foi implementada uma função de detecção de idioma baseada em termos característicos de português e inglês presentes no texto da issue.

**Solução encontrada:**

O processamento passou a selecionar o modelo correspondente ao idioma identificado:

* `en_core_web_sm` para inglês;
* `pt_core_news_sm` para português.

No corpus final, foram identificadas **210 issues em inglês e 70 em português**.

**O que aprendemos:**

A escolha do modelo de PLN deve considerar as características do corpus. Trabalhar com um corpus bilíngue exigiu que o processamento fosse adaptado para utilizar modelos diferentes dentro do mesmo pipeline.

---

## Entrada 8

**Data:** dia 4 do desenvolvimento
**Componente:** PLN com spaCy
**Problema:** Definição das etapas de processamento linguístico.

**O que aconteceu:**

Era necessário transformar o texto bruto das issues em informações linguísticas que pudessem ser utilizadas posteriormente na análise do projeto.

**Tentativa de solução:**

Estruturamos o processamento utilizando as funcionalidades do spaCy previstas para a etapa de PLN: tokenização, lematização, remoção de stopwords, identificação de classes gramaticais e extração de entidades.

**Solução encontrada:**

O módulo `nlp.py` passou a realizar as seguintes etapas:

1. identificação do idioma;
2. tokenização;
3. lematização;
4. remoção de stopwords;
5. identificação de POS;
6. extração de entidades nomeadas.

Os resultados foram organizados no arquivo `resultados/nlp_results.csv`.

**O que aprendemos:**

O processamento linguístico transforma o texto bruto em diferentes representações que podem ser utilizadas nas etapas posteriores. Cada etapa possui uma finalidade diferente e, juntas, permitem analisar tanto a estrutura quanto o conteúdo linguístico das issues.

---

## Entrada 9

**Data:** dia 4 do desenvolvimento
**Componente:** PLN com spaCy
**Problema:** Entidades reconhecidas incorretamente em textos técnicos.

**O que aconteceu:**

Durante a validação dos resultados, percebemos que o modelo do spaCy reconhecia alguns elementos técnicos, como versões, números de issues, identificadores e nomes de funções, como entidades de categorias como `CARDINAL`, `ORG` ou `MISC`.

Isso acontece porque o corpus contém muitos elementos próprios de código e documentação técnica.

**Tentativa de solução:**

Analisamos a distribuição das entidades e alguns exemplos reais produzidos pelo modelo para verificar se o processamento estava funcionando e se os resultados estavam sendo registrados corretamente.

**Solução encontrada:**

Mantivemos a extração de entidades do spaCy como uma etapa de processamento linguístico geral, sem tentar corrigir manualmente cada classificação feita pelo modelo.

A análise final identificou **5.705 entidades** no conjunto de 280 issues.

**O que aprendemos:**

Modelos de PLN treinados para linguagem geral podem apresentar limitações quando aplicados a textos técnicos. Nem toda classificação de entidade será perfeita em uma issue de software, mas o resultado ainda pode ser útil como parte do processamento linguístico, desde que suas limitações sejam consideradas na interpretação.

---

## Entrada 10

**Data:** dia 4 do desenvolvimento
**Componente:** PLN com spaCy
**Problema:** Validação do resultado final do processamento.

**O que aconteceu:**

Depois da implementação do `nlp.py`, foi necessário verificar se todas as etapas estavam sendo executadas e se o arquivo de resultados possuía as informações esperadas.

**Tentativa de solução:**

Executamos o processamento completo das 280 issues e posteriormente carregamos o arquivo `resultados/nlp_results.csv` com pandas para conferir as colunas e os primeiros registros.

**Solução encontrada:**

O processamento foi concluído com sucesso, gerando:

* **280 issues analisadas**
* **210 issues em inglês**
* **70 issues em português**
* **101.509 tokens**
* **5.705 entidades**

O arquivo final contém as colunas:

`repositorio`, `numero`, `titulo`, `idioma`, `tokens`, `lemmas`, `sem_stopwords`, `pos` e `entidades`.

**O que aprendemos:**

Além de verificar se o programa executa sem erros, é necessário validar os dados produzidos. A inspeção dos registros finais permitiu confirmar que as diferentes etapas do processamento estavam sendo armazenadas corretamente e que os resultados poderiam ser utilizados pelas próximas etapas do projeto.

---

## Entrada 11

**Data:** dia 4 do desenvolvimento
**Componente:** Regex e PLN
**Problema:** Integração dos resultados com as próximas etapas do projeto.

**O que aconteceu:**

Ao finalizar os componentes de Regex e spaCy, os resultados passaram a ser utilizados como entrada para as etapas seguintes do projeto, principalmente para a análise dos padrões encontrados nas issues.

**Tentativa de solução:**

Organizamos os resultados em arquivos CSV separados, mantendo os dados derivados da análise Regex e do processamento linguístico.

**Solução encontrada:**

Foram finalizados:

* `src/regex.py`
* `src/nlp.py`
* `resultados/regex_results.csv`
* `resultados/nlp_results.csv`

Os arquivos ficaram preparados para serem utilizados pela etapa de análise e pela integração do projeto.

**O que aprendemos:**

Um projeto de processamento de dados depende da integração entre as etapas. É importante que cada componente tenha entradas e saídas bem definidas para que o trabalho de uma pessoa possa ser utilizado pelos demais integrantes sem necessidade de refazer o processamento.

---

## Considerações finais

A etapa de processamento textual permitiu aplicar Regex e spaCy sobre um corpus real de **280 issues do GitHub**. Durante o desenvolvimento, foi necessário não apenas implementar os padrões, mas também validar os resultados e ajustar o processamento para lidar com características específicas de textos de software, como versões, códigos, URLs, referências, números e diferentes idiomas.

Com o Regex, foram identificados padrões técnicos relacionados a versões, referências, erros, caminhos de arquivos, URLs e urgência. Com o spaCy, as issues foram processadas linguisticamente por meio de tokenização, lematização, remoção de stopwords, POS e reconhecimento de entidades.

A principal aprendizagem dessa etapa foi perceber que o processamento de textos reais exige validação e refinamento contínuos. Os resultados obtidos pelos modelos e padrões não devem ser considerados automaticamente corretos: é necessário analisar o contexto dos dados, identificar falsos positivos e compreender as limitações das ferramentas utilizadas.
