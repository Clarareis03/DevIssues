# Diário de bordo — DevIssues

**Integrante:** Ayra Souza
**Data:** 26/09/2026
**Componente:** Coleta de dados (GitHub API)

---

## Entrada 1

**Data:** dia 1 do desenvolvimento
**Componente:** Coleta
**Problema:** Configuração do token de acesso à API do GitHub.

**O que aconteceu:**
Sem token, a API do GitHub limita a 60 requisições por hora — insuficiente para coletar centenas de issues. Também havia dúvida sobre qual tipo de token usar: o clássico ("classic") ou o novo, por permissões ("fine-grained").

**Tentativa de solução:**
Pesquisamos a diferença entre os dois tipos de token e as permissões que cada um concede.

**Solução encontrada:**
Optamos pelo token *fine-grained*, com "Repository access" definido como **"Public Repositories (read-only)"**. Essa opção é mais segura por dar apenas leitura (nunca escrita) e não exige selecionar permissões extras, já que o acesso de leitura a repositórios públicos já vem incluso.

**O que aprendemos:**
Tokens de acesso devem seguir o princípio do menor privilégio: como o projeto só lê dados públicos, não faz sentido usar um token com permissão de escrita. Também aprendemos a nunca deixar o token escrito no código-fonte, guardando-o em uma variável de ambiente (arquivo `.env`, listado no `.gitignore`).

---

## Entrada 2

**Data:** dia 1 do desenvolvimento
**Componente:** Coleta
**Problema:** `pip install -r requirements.txt` não encontrava o arquivo.

**O que aconteceu:**
O terminal informava `ERROR: Could not open requirements file: [Errno 2] No such file or directory`.

**Tentativa de solução:**
Conferimos o conteúdo da pasta com o comando `dir`.

**Solução encontrada:**
O download do repositório havia criado uma pasta duplicada (`DevIssues\DevIssues`), e o terminal estava aberto um nível acima de onde os arquivos realmente estavam. Um simples `cd DevIssues` resolveu.

**O que aprendemos:**
Sempre conferir o diretório de trabalho atual do terminal antes de rodar comandos que dependem de arquivos locais, principalmente depois de baixar ou extrair arquivos de outro lugar.

---

## Entrada 3

**Data:** dia 1 do desenvolvimento
**Componente:** Coleta
**Problema:** Arquivos `.env.example` e `.gitignore` perderam o ponto inicial do nome.

**O que aconteceu:**
Ao salvar os arquivos manualmente, eles apareceram no VS Code como `env.example` e `gitignore`, sem o ponto. Sem o ponto, o `.gitignore` não é reconhecido pelo Git e não tem efeito nenhum.

**Tentativa de solução:**
Verificamos os nomes dos arquivos na árvore do VS Code.

**Solução encontrada:**
Renomeamos os arquivos manualmente (clique direito → Rename), adicionando o ponto no início do nome.

**O que aprendemos:**
Arquivos que começam com ponto (arquivos "ocultos"/de configuração) às vezes são renomeados sem querer por editores de texto ou pelo navegador ao salvar. Vale sempre conferir o nome exato depois de criar esse tipo de arquivo.

---

## Entrada 4

**Data:** dia 2 do desenvolvimento
**Componente:** Coleta
**Problema:** Repositório `frontendbr/open-source` retornou erro 404 (não encontrado) ao coletar.

**O que aconteceu:**
A ideia inicial era incluir esse repositório para ter uma amostra de issues em português. Ao rodar a coleta, a API devolveu `404 Client Error: Not Found`, mesmo o repositório aparecendo em buscas e links antigos.

**Tentativa de solução:**
Pesquisamos se o repositório havia sido renomeado, tornado privado ou removido.

**Solução encontrada:**
Substituímos por `filipedeschamps/tabnews.com.br` (TabNews), um projeto brasileiro confirmado como público e ativo, com bom volume de issues em português.

**O que aprendemos:**
Nem todo repositório listado como "ativo" numa busca continua acessível pela API — é importante testar o repositório real antes de fixá-lo na coleta final, e ter um plano B caso a fonte escolhida mude de status.

---

## Entrada 5

**Data:** dia 2 do desenvolvimento
**Componente:** Coleta
**Problema:** `PermissionError: [Errno 13] Permission denied` ao salvar `dados/issues.csv`.

**O que aconteceu:**
A coleta rodou normalmente (as 280 issues dos 4 repositórios foram buscadas com sucesso), mas o programa quebrou na hora de escrever o arquivo CSV, e o arquivo ficou vazio.

**Tentativa de solução:**
Verificamos se o arquivo estava aberto em outro programa (Excel, aba de preview) e se estava marcado como "somente leitura".

**Solução encontrada:**
Apagamos o arquivo `dados/issues.csv` manualmente e rodamos o programa de novo, deixando-o recriar o arquivo do zero. Funcionou.

**O que aprendemos:**
No Windows, um arquivo pode ficar temporariamente bloqueado por outro processo (editor, sincronização com nuvem, indexação), impedindo a escrita mesmo quando o código está correto. Quando isso acontece, apagar e deixar o programa recriar o arquivo costuma resolver. Também aprendemos que um erro na etapa de salvar não significa que a coleta em si falhou — os dados já haviam sido buscados corretamente na API.

---

## Entrada 6

**Data:** dia 2 do desenvolvimento
**Componente:** Coleta
**Problema:** Mistura de idiomas nos dados coletados (inglês e português).

**O que aconteceu:**
Ao incluir o `tabnews.com.br` (issues em português) junto com `psf/requests`, `pandas-dev/pandas` e `microsoft/vscode` (issues em inglês), percebemos que o corpus final ficaria bilíngue.

**Tentativa de solução:**
Discutimos como isso afetaria o componente de spaCy, já que o modelo do spaCy é específico por idioma (`en_core_web_sm` para inglês, `pt_core_news_sm` para português).

**Solução encontrada:**
Decidimos manter o corpus bilíngue como característica do projeto, cabendo ao componente de PLN separar as issues por idioma (usando o campo `repositorio` do CSV) antes de aplicar o modelo correto a cada bloco.

**O que aprendemos:**
Decisões tomadas na etapa de coleta impactam diretamente os componentes seguintes do pipeline. Importante documentar essas decisões (como esta) para que quem for implementar o spaCy já saiba lidar com os dois idiomas, em vez de descobrir isso só na hora de rodar.

---