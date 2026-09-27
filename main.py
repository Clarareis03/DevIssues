"""
DevIssues — main.py
Ponto de entrada principal da aplicação.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path para garantir
# que as importações do pacote 'src' funcionem de forma consistente
DIRETORIO_RAIZ = Path(__file__).resolve().parent
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

# Garante a criação das pastas do projeto
(DIRETORIO_RAIZ / "dados").mkdir(exist_ok=True)
(DIRETORIO_RAIZ / "resultados").mkdir(exist_ok=True)

from src.interface import executar_menu

if __name__ == "__main__":
    try:
        executar_menu()
    except KeyboardInterrupt:
        print("\n\n[!] Execução interrompida pelo utilizador. Até breve!")
        sys.exit(0)