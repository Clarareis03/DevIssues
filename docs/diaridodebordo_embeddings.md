# Diário de bordo — DevIssues (2ª etapa)

**Integrante:** Ana Beatriz Sena

**Data:** 16/11/2026

**Componente:** Embeddings (`src/embeddings.py`)

---

## Entrada 1

**Data:** 16/11/2026

**Componente:** Ambiente de desenvolvimento

**Problema:** Preparar o ambiente Python para trabalhar com embeddings e processamento vetorial.

**O que aconteceu:**

Para implementar a geração de embeddings, foi necessário configurar as bibliotecas de processamento de dados, aprendizado de máquina e processamento de linguagem natural. Também foi necessário garantir que o VS Code estivesse utilizando o ambiente virtual correto.

**Tentativa de solução:**

Instalamos as dependências necessárias e verificamos a disponibilidade das bibliotecas no ambiente virtual do projeto.

**Solução encontrada:**

Configuramos o ambiente `.venv-1` e instalamos as bibliotecas NumPy, Pandas, Matplotlib, Scikit-learn, Sentence Transformers e PyTorch. Também ajustamos o interpretador Python do VS Code para utilizar esse ambiente.

**O que aprendemos:**

O ambiente virtual mantém as dependências organizadas e evita conflitos entre versões de bibliotecas. Também aprendemos que o interpretador selecionado no VS Code precisa corresponder ao ambiente em que as dependências foram instaladas.

---

## Entrada 2

**Data:** 16/11/2026

**Componente:** Geração de embeddings

**Problema:** Transformar as 280 issues em representações numéricas que preservassem suas características semânticas.

**O que aconteceu:**

A base do projeto contém issues em português e inglês. Para realizar comparações semânticas entre os textos, precisávamos utilizar um modelo capaz de trabalhar com os dois idiomas.

**Tentativa de solução:**

Pesquisamos modelos disponíveis no Sentence Transformers e selecionamos um modelo multilíngue para representar os textos.

**Solução encontrada:**

Utilizamos o modelo `paraphrase-multilingual-MiniLM-L12-v2`. Os títulos e corpos das issues foram combinados por meio da função `montar_texto_issue()`, já existente em `src/nlp.py`.

A geração foi realizada com `normalize_embeddings=True`, produzindo uma matriz de 280 issues por 384 dimensões.

O resultado foi salvo em `resultados/embeddings.npy`.

**O que aprendemos:**

Embeddings transformam textos em vetores numéricos que permitem comparar suas representações sem depender exclusivamente de palavras iguais. Também entendemos a importância de escolher um modelo compatível com os idiomas presentes na base.

---

## Entrada 3

**Data:** 16/11/2026

**Componente:** Busca semântica

**Problema:** Encontrar issues relacionadas a uma consulta mesmo quando elas não utilizam exatamente as mesmas palavras.

**O que aconteceu:**

A proposta era permitir que uma pessoa pesquisasse um problema utilizando linguagem natural e encontrasse issues com conteúdos semanticamente próximos.

**Tentativa de solução:**

Implementamos uma função que transforma a consulta em um embedding e compara sua representação com os vetores das 280 issues.

**Solução encontrada:**

Criamos a função `buscar_issues_semelhantes()`, utilizando a similaridade do cosseno para comparar os vetores.

A função ordena os resultados pela similaridade e retorna as cinco issues mais próximas da consulta.

No primeiro experimento, utilizamos:

`Error when connecting to database`

A busca retornou cinco resultados, com similaridades aproximadas entre 0,398 e 0,472.

**O que aprendemos:**

A similaridade do cosseno permite identificar proximidade entre representações vetoriais. Entretanto, uma pontuação alta não garante que o resultado seja realmente relevante para a consulta. A leitura dos resultados continua sendo necessária para avaliar a qualidade da busca.

---

## Entrada 4

**Data:** 16/11/2026

**Componente:** Agrupamento com KMeans

**Problema:** Identificar grupos de issues que apresentassem características semânticas semelhantes.

**O que aconteceu:**

Após gerar os embeddings, precisávamos explorar se os vetores poderiam revelar padrões temáticos entre as issues, inclusive entre diferentes repositórios.

**Tentativa de solução:**

Aplicamos o algoritmo KMeans sobre a matriz de embeddings, inicialmente definindo quatro agrupamentos.

**Solução encontrada:**

Implementamos a função `agrupar_issues()`, utilizando os parâmetros `n_clusters=4`, `random_state=42` e `n_init=10`.

A execução distribuiu as 280 issues da seguinte forma:

- Cluster 0: 102 issues (36,4%).
- Cluster 1: 52 issues (18,6%).
- Cluster 2: 59 issues (21,1%).
- Cluster 3: 67 issues (23,9%).

Os resultados foram exportados para `resultados/embeddings_resultados.csv`.

**O que aprendemos:**

O KMeans permite organizar os textos em grupos a partir de suas representações vetoriais. Entretanto, o algoritmo não atribui automaticamente um significado aos grupos. É necessário analisar os textos para interpretar os temas encontrados.

---

## Entrada 5

**Data:** 16/11/2026

**Componente:** Visualização com PCA

**Problema:** Representar visualmente embeddings que possuem 384 dimensões.

**O que aconteceu:**

A quantidade de dimensões dos embeddings impossibilita sua representação direta em um gráfico convencional de duas dimensões.

**Tentativa de solução:**

Utilizamos a técnica PCA (*Principal Component Analysis*) para reduzir a dimensionalidade dos vetores.

**Solução encontrada:**

Implementamos a função `aplicar_pca()`, reduzindo os embeddings para duas componentes principais.

As duas dimensões explicaram conjuntamente 17,32% da variância dos dados. Em seguida, criamos um gráfico de dispersão que identifica cada issue de acordo com seu cluster.

O gráfico foi salvo em `resultados/clusters_pca.png`.

**O que aprendemos:**

O PCA permite representar dados de alta dimensionalidade em um espaço visual mais simples. Porém, a redução para duas dimensões provoca perda de informação, portanto o gráfico não representa integralmente as relações existentes no espaço original dos embeddings.

---

## Entrada 6

**Data:** 16/11/2026

**Componente:** Validação qualitativa dos clusters

**Problema:** Verificar se os agrupamentos gerados pelo KMeans apresentavam coerência temática.

**O que aconteceu:**

Após a geração dos quatro clusters, percebemos que a distribuição numérica não era suficiente para compreender o significado dos agrupamentos. Precisávamos investigar o conteúdo das issues.

**Tentativa de solução:**

Selecionamos uma amostra aleatória de 15 issues por cluster, totalizando 60 issues. Analisamos os títulos e os primeiros 500 caracteres das descrições para identificar assuntos recorrentes.

**Solução encontrada:**

A leitura permitiu identificar os seguintes temas provisórios:

- Cluster 0: funcionalidades, configurações e integrações de software.
- Cluster 1: comportamento interno, manipulação e conversão de dados no Pandas.
- Cluster 2: evolução das funcionalidades e experiência de uso.
- Cluster 3: correção de comportamentos, confiabilidade e compatibilidade técnica.

O Cluster 0 apresentou maior heterogeneidade, enquanto os demais demonstraram características temáticas mais facilmente identificáveis na amostra.

**O que aprendemos:**

A interpretação dos clusters depende da análise dos textos originais. Os grupos são formados matematicamente, mas seus significados precisam ser identificados por meio da leitura e interpretação humana.

---

## Entrada 7

**Data:** 16/11/2026

**Componente:** Análise exploratória — repositórios e idiomas

**Problema:** Investigar se os agrupamentos estavam relacionados ao idioma ou ao repositório de origem das issues.

**O que aconteceu:**

Durante a análise dos clusters, observamos que alguns agrupamentos estavam concentrados em determinados repositórios. Também percebemos diferenças na distribuição dos idiomas.

Para investigar essas relações, construímos tabelas cruzadas e calculamos o V de Cramér.

**Tentativa de solução:**

Comparamos três associações: cluster e idioma, cluster e repositório, e repositório e idioma.

**Solução encontrada:**

Os resultados foram:

- Cluster × idioma: V = 0,707.
- Cluster × repositório: V = 0,695.
- Repositório × idioma: V = 1,000.

A associação perfeita entre repositório e idioma ocorreu porque todas as 70 issues do TabNews estavam em português, enquanto as 210 issues dos demais repositórios estavam em inglês.

**O que aprendemos:**

A composição da base influencia a interpretação dos agrupamentos. Como repositório e idioma estão completamente associados, não é possível isolar a influência de cada variável nos clusters. Por isso, precisamos ter cuidado ao afirmar que o modelo agrupou as issues exclusivamente por características semânticas.

---

## Entrada 8

**Data:** 16/11/2026

**Componente:** Avaliação quantitativa do KMeans

**Problema:** Avaliar matematicamente a qualidade dos agrupamentos gerados.

**O que aconteceu:**

A análise qualitativa identificou temas recorrentes nos clusters, mas ainda precisávamos avaliar a separação matemática entre os grupos.

**Tentativa de solução:**

Calculamos três métricas utilizando os embeddings originais e os rótulos produzidos pelo KMeans:

- Silhouette Score;
- Davies-Bouldin Index;
- Calinski-Harabasz Index.

**Solução encontrada:**

Para a configuração com quatro clusters, obtivemos:

| Métrica | Resultado |
|---|---:|
| Silhouette Score | 0,0886 |
| Davies-Bouldin Index | 3,5811 |
| Calinski-Harabasz Index | 18,6928 |

Os resultados indicaram limitações na separação matemática dos agrupamentos, apesar da identificação de temas recorrentes na análise qualitativa.

**O que aprendemos:**

A avaliação de um agrupamento não deve depender apenas da interpretação visual ou da leitura de uma amostra. É importante combinar métricas quantitativas e análise qualitativa para compreender melhor os resultados.

---

## Entrada 9

**Data:** 16/11/2026

**Componente:** Comparação de configurações do KMeans

**Problema:** Verificar se a escolha de quatro clusters era adequada para a base analisada.

**O que aconteceu:**

Após calcular as métricas da configuração inicial, percebemos que seria interessante comparar diferentes quantidades de agrupamentos para entender como a estrutura dos resultados se comportava.

**Tentativa de solução:**

Testamos sete configurações do KMeans, variando a quantidade de clusters entre 2 e 8. Para cada configuração, calculamos as três métricas de avaliação e construímos gráficos para comparar seus comportamentos.

**Solução encontrada:**

Os resultados mostraram que não existia uma configuração claramente superior em todos os indicadores.

- K=7 apresentou o maior Silhouette Score: 0,0934.
- K=2 apresentou o menor Davies-Bouldin Index: 2,0755.
- K=2 apresentou o maior Calinski-Harabasz Index: 29,8026.

A configuração K=4 foi mantida como referência para a análise principal, considerando a interpretabilidade temática dos quatro agrupamentos, sem afirmar que fosse a configuração matematicamente ideal.

**O que aprendemos:**

A escolha da quantidade de clusters envolve mais do que encontrar o melhor resultado em uma métrica isolada. Também é necessário considerar o objetivo da análise e a utilidade dos agrupamentos para interpretar os dados.

---

## Registro final

O desenvolvimento de Embeddings permitiu transformar as 280 issues do projeto em representações vetoriais, implementar uma busca semântica e explorar agrupamentos por meio do KMeans.

Durante o processo, também foram realizadas análises qualitativas e quantitativas para investigar a coerência dos resultados e compreender suas limitações.

Um dos principais aprendizados foi perceber que a aplicação de modelos de linguagem não termina na execução do algoritmo. É necessário investigar os resultados, questionar as métricas e compreender as características da base antes de tirar conclusões.

**Status:** Implementação e análise exploratória concluídas. Documentação e integração final ao projeto pendentes.