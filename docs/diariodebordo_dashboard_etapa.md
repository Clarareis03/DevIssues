# Diário de bordo — DevIssues (2ª etapa)

**Integrante:** Maria Clara Reis  
**Data:** 17/11/2026  
**Componente:** Integração dos resultados e Dashboard Streamlit

---

## Entrada 1 — Integração dos componentes

**Data:** 17/11/2026  
**Componente:** Integração de dados

**Problema:** Integrar os resultados das três trilhas da segunda etapa em uma única aplicação.

**O que aconteceu:**  
Os componentes de spaCy avançado, Embeddings e Transformers já estavam implementados separadamente. Entretanto, o dashboard ainda apresentava principalmente as análises da primeira etapa.

**Tentativa de solução:**  
Analisamos a estrutura do repositório e identificamos os arquivos CSV gerados pelos novos módulos, buscando uma forma de integrá-los sem modificar os códigos das demais integrantes.

**Solução encontrada:**  
Criamos o arquivo `src/integracao_etapa2.py`, responsável por localizar, carregar e verificar os resultados. O teste confirmou a existência de cinco arquivos principais, cada um contendo 280 registros.

**O que aprendemos:**  
A separação entre processamento e visualização facilita a integração de componentes desenvolvidos por diferentes integrantes e permite reutilizar resultados sem executar novamente os modelos.

---

## Entrada 2 — Conflito de portas no Streamlit

**Data:** 17/11/2026  
**Componente:** Ambiente de execução

**Problema:** Ao tentar abrir o dashboard do DevIssues, o navegador apresentava outra aplicação, chamada Lucia Analytics.

**O que aconteceu:**  
A outra aplicação estava sendo acessada pela porta 8501, utilizada por padrão pelo Streamlit, causando confusão ao abrir o endereço local.

**Tentativa de solução:**  
Verificamos o endereço acessado no navegador e identificamos a necessidade de executar o DevIssues em outra porta.

**Solução encontrada:**  
Iniciamos a aplicação com o comando:

`python -m streamlit run app.py --server.port 8502`

O DevIssues passou a funcionar corretamente em `http://localhost:8502`.

**O que aprendemos:**  
Diferentes aplicações locais precisam utilizar portas disponíveis e distintas. Configurar explicitamente a porta ajuda a evitar conflitos durante o desenvolvimento.

---

## Entrada 3 — Integração das análises ao dashboard

**Data:** 17/11/2026  
**Componente:** Interface Streamlit

**Problema:** Os resultados da segunda etapa estavam disponíveis em arquivos separados e não podiam ser explorados diretamente pela interface principal.

**O que aconteceu:**  
Inicialmente, adicionamos três abas ao dashboard existente, correspondentes às trilhas de spaCy avançado, Embeddings e Transformers.

**Tentativa de solução:**  
Utilizamos os arquivos CSV já produzidos para construir tabelas, indicadores e gráficos, sem recalcular os resultados dos modelos.

**Solução encontrada:**  
As três áreas foram integradas ao Streamlit, permitindo visualizar entidades reconhecidas, agrupamentos semânticos e classificações de sentimento.

**O que aprendemos:**  
O Streamlit permite integrar diferentes resultados analíticos em uma mesma aplicação, facilitando a interpretação e a demonstração dos métodos utilizados.

---

## Entrada 4 — Reformulação visual da interface

**Data:** 17/11/2026  
**Componente:** Design e experiência do usuário

**Problema:** A primeira versão integrada do dashboard apresentava muitas tabelas e informações simultaneamente, prejudicando a organização visual.

**O que aconteceu:**  
A interface continha seções extensas, gráficos e mensagens explicativas, tornando a navegação menos objetiva.

**Tentativa de solução:**  
Reorganizamos a apresentação dos resultados, priorizando indicadores resumidos, navegação por páginas e visualizações gráficas.

**Solução encontrada:**  
O `app.py` foi reformulado com identidade visual escura e roxa, cards de indicadores, gráficos interativos, menu lateral e páginas dedicadas às diferentes análises. Tabelas detalhadas passaram a ocupar áreas recolhíveis, reduzindo a quantidade de informações exibidas simultaneamente.

**O que aprendemos:**  
A visualização de dados não depende apenas da construção de gráficos. A organização das informações, a hierarquia visual e a navegação são importantes para tornar os resultados compreensíveis.

---

## Entrada 5 — Dependência da busca semântica

**Data:** 17/11/2026  
**Componente:** Embeddings e busca semântica

**Problema:** Ao testar a busca semântica pela interface, ocorreu o erro `ModuleNotFoundError: No module named 'sentence_transformers'`.

**O que aconteceu:**  
A biblioteca necessária para carregar o modelo de embeddings não estava disponível no ambiente Python utilizado pelo Streamlit.

**Tentativa de solução:**  
Verificamos a dependência utilizada pelo módulo `src/embeddings.py` e a necessidade de instalá-la no mesmo interpretador Python responsável pela execução da aplicação.

**Solução encontrada:**  
Utilizamos o comando `python -m pip install sentence-transformers` e reiniciamos o Streamlit. Após o ajuste, o funcionamento da busca semântica foi confirmado.

**O que aprendemos:**  
Ter uma biblioteca declarada no `requirements.txt` não garante que ela esteja instalada no ambiente ativo. É importante manter consistência entre o interpretador Python, as dependências e a aplicação.

---

## Registro final

A integração da segunda etapa permitiu reunir os resultados de spaCy avançado, Embeddings e Transformers em uma interface única, organizada e interativa.

Além da integração técnica, o desenvolvimento envolveu resolução de problemas de ambiente, instalação de dependências e reformulação da experiência visual do dashboard.

O principal aprendizado foi compreender que a entrega de um projeto de análise de dados envolve não apenas a implementação dos modelos, mas também sua integração, apresentação e utilização por outras pessoas.

**Status:** Integração e reformulação visual concluídas, com execução local confirmada. Avaliação manual dos Transformers ainda pendente.