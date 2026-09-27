# Diário de bordo — DevIssues

**Integrante:** Maria Clara Reis 
**Data:** 26/09/2026  
**Componente:** Análise e Interface (Streamlit)  

---

## Entrada 1

**Data:** dia 1 do desenvolvimento  
**Componente:** Análise  
**Problema:** Erro de importação de módulos (`ModuleNotFoundError: No module named 'src'`).  

**O que aconteceu:**  
Ao tentar executar os scripts `analise.py` e `interface.py` diretamente pelo terminal ou no VS Code, o Python definia a subpasta `src` como diretório de execução e não encontrava o pacote `src.` referenciado nos imports.  

**Tentativa de solução:**  
Alterar manualmente os caminhos das pastas e rodar os arquivos de dentro de diretórios diferentes.  

**Solução encontrada:**  
Criamos o ponto de entrada `main.py` na raiz do projeto ajustando o `sys.path` dinamicamente, além de implementar tratamento com bloco `try/except` nas importações e orientar a execução de módulos via `-m` (`python -m src.interface`).  

**O que aprendemos:**  
O funcionamento da resolução de módulos do Python depende de como o script é invocado. Estruturar um ponto de entrada na raiz garante a consistência do `sys.path` em qualquer ambiente.  

---

## Entrada 2

**Data:** dia 2 do desenvolvimento  
**Componente:** Análise  
**Problema:** Inconsistência e "falsos neutros" na análise de sentimento baseada nos lemas do spaCy.  

**O que aconteceu:**  
A comparação de texto não considerava termos em maiúsculas ou variações morfológicas das palavras, resultando em muitas issues sendo classificadas erroneamente como "Neutro".  

**Tentativa de solução:**  
Criar listas extensas de palavras inteiras em strings sem aproveitar o processamento do spaCy.  

**Solução encontrada:**  
Padronizamos a normalização dos lemas gerados pelo spaCy para letras minúsculas antes de cruzá-los com dicionários de polaridade, combinando o resultado do sentimento com as labels nativas do GitHub e as métricas do Regex para definir categorias como Bugs, Urgência e Dívida Técnica.  

**O que aprendemos:**  
A lematização do spaCy reduz drasticamente a variação das palavras para a sua forma base, mas requer uma etapa de tratamento e normalização das strings para garantir cruzamentos precisos com dicionários de regras.  

---

## Entrada 3

**Data:** dia 2 do desenvolvimento  
**Componente:** Interface  
**Problema:** Limitações visuais e fluxo confuso da interface em terminal.  

**O que aconteceu:**  
A interface inicial em linha de comando era limitada para exibir visualmente dados estatísticos, além de exigir navegação por menus manuais e reprocessamento contínuo dos dados a cada execução.  

**Tentativa de solução:**  
Implementar caracteres ASCII para desenhar barras de progresso no terminal.  

**Solução encontrada:**  
Migramos a camada de apresentação para o **Streamlit** (`app.py`), construindo um Dashboard web interativo que carrega diretamente o arquivo de resultados `resultados/relatorio_final.csv`.  

**O que aprendemos:**  
Ferramentas de prototipagem web focadas em dados proporcionam uma experiência de usuário (UX) infinitamente superior para a visualização de métricas de software sem adicionar complexidade excessiva de código frontend.  

---

## Entrada 4

**Data:** dia 3 do desenvolvimento  
**Componente:** Interface  
**Problema:** Risco de falhas e lentidão ao tentar rodar novas coletas ou processamentos pesados ao vivo durante a apresentação.  

**O que aconteceu:**  
A versão inicial da aplicação web continha menus laterais com formulários para "Nova Coleta" e "Executar Análise", o que dispersava o foco e trazia o risco de demoras ou falhas de conexão com a API do GitHub no momento da demonstração.  

**Tentativa de solução:**  
Ocultar abas secundárias da barra lateral do Streamlit.  

**Solução encontrada:**  
Redesenhamos a interface como uma **página única contínua (Single-Page App)**, focada em duas seções principais: 1. Dashboard de Métricas com tabela de filtros interativos em tempo real; e 2. Seção de Metodologia Técnica estruturada em abas (`st.tabs`) para detalhar a contribuição de cada integrante do grupo.  

**O que aprendemos:**  
Interfaces destinadas a demonstrações técnicas e acadêmicas devem priorizar a clareza na exibição dos resultados e no entendimento da arquitetura, eliminando fluxos redundantes que possam comprometer a fluidez da apresentação.