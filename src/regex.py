"""
DevIssues - Análise de Issues do GitHub com Regex

Este módulo identifica padrões linguísticos e técnicos em issues:
- versões;
- referências a issues/PRs;
- erros e exceções;
- caminhos de arquivos;
- URLs;
- termos explícitos de urgência.

A análise é realizada sobre o título + corpo das issues.
"""

import csv
import re
from pathlib import Path


# ============================================================
# PADRÕES REGEX
# ============================================================

# Versões de software.
#
# Exemplos:
# 3.12
# 3.12.1
# v3.12.1
# 2.34.2
# 6.8.0-136-generic
# 22.04.1-Ubuntu
PADRAO_VERSAO = (
    r"(?<![\d.])"
    r"v?\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?"
    r"(?!\.\d)"
)

# Endereço IPv4.
PADRAO_IP_COMPLETO = (
    r"(?<!\d)"
    r"(?:\d{1,3}\.){3}\d{1,3}"
    r"(?!\d)"
)

# Padrões de redes que podem gerar falsos positivos.
PADRAO_REDE = (
    r"(?i)\b(?:"
    r"10(?:\.\d{1,3})?(?:\.x){0,2}"
    r"|172\.16-31(?:\.x){0,1}"
    r"|192\.168(?:\.x){0,2}"
    r"|169\.254(?:\.x){0,2}"
    r"|127(?:\.0){0,2}(?:\.x)?"
    r")\b"
)

# Referências a issues/PRs.
# Exemplo: #1234
PADRAO_REFERENCIA = r"(?<!\w)#\d+\b"

# Erros e exceções.
# Exemplos: ValueError, TypeError, AttributeError.
PADRAO_ERRO = r"\b[A-Za-z_]\w*(?:Error|Exception)\b"

# Caminhos de arquivos.
PADRAO_CAMINHO = (
    r"(?<![\w./-])"
    r"(?:\.?[\w.-]+/)+"
    r"[\w.-]+\."
    r"(?:py|js|ts|tsx|jsx|java|go|rs|cpp|c|h|hpp|"
    r"md|rst|yml|yaml|json|toml|ini|txt|html|css|vue|rb|php|sh)"
    r"\b"
)

# URLs HTTP/HTTPS.
PADRAO_URL = r"https?://[^\s<>\")\']+"

# Termos explícitos de urgência.
PADRAO_URGENCIA = (
    r"\b(?:urgent|urgently|critical|asap|blocking|blocked|"
    r"high priority|release blocker|blocker)\b"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def texto_seguro(texto):
    """Garante que o valor analisado seja uma string."""
    if texto is None:
        return ""

    return str(texto)


def _parece_endereco_ip(valor):
    """
    Verifica se o valor corresponde a um endereço IPv4.

    Exemplo:
        192.168.1.10 -> True
        3.12.1 -> False
    """
    partes = valor.split(".")

    if len(partes) != 4:
        return False

    if not all(parte.isdigit() for parte in partes):
        return False

    return all(
        0 <= int(parte) <= 255
        for parte in partes
    )


def _contexto_versao(texto, inicio, fim):
    """
    Verifica se uma ocorrência decimal possui contexto
    relacionado a versão de software.

    Isso permite reconhecer casos como:

        OpenSSL 4.0
        Python 3.12
        version 3.13
        Ubuntu 22.04
    """

    inicio_contexto = max(0, inicio - 60)
    fim_contexto = min(len(texto), fim + 40)

    contexto = texto[
        inicio_contexto:fim_contexto
    ].lower()

    marcadores = (
        "version",
        "version:",
        "versão",
        "release",
        "python",
        "node",
        "npm",
        "pip",
        "openssl",
        "django",
        "requests",
        "urllib",
        "pandas",
        "numpy",
        "flask",
        "pytest",
        "package",
        "packages",
        "dependency",
        "dependencies",
        "driver",
        "browser",
        "chrome",
        "firefox",
        "ubuntu",
        "debian",
        "linux",
        "windows",
        "macos",
        "kernel",
        "gcc",
        "clang",
        "postgres",
        "postgresql",
        "mysql",
        "redis",
        "docker",
        "kubernetes",
        "library",
        "libraries",
        "software",
        "tool",
    )

    return any(
        marcador in contexto
        for marcador in marcadores
    )


def _esta_em_contexto_de_rede(texto, inicio, fim):
    """
    Identifica ocorrências próximas de termos relacionados
    a endereços IP e redes.
    """

    inicio_contexto = max(0, inicio - 50)
    fim_contexto = min(len(texto), fim + 50)

    contexto = texto[
        inicio_contexto:fim_contexto
    ].lower()

    marcadores = (
        "ip",
        "ipv4",
        "ipv6",
        "network",
        "networks",
        "networking",
        "subnet",
        "subnetting",
        "localhost",
        "loopback",
        "private network",
        "private networks",
        "rfc 1918",
        "ip address",
        "ip addresses",
    )

    return any(
        marcador in contexto
        for marcador in marcadores
    )


def _parece_secao_rfc(texto, inicio):
    """
    Identifica números que representam seções de RFC.

    Exemplos que devem ser ignorados:

        §15.2.3
        RFC 9110 §15.2.4
        section 15.2.3
    """

    inicio_contexto = max(0, inicio - 40)

    contexto = texto[
        inicio_contexto:inicio
    ].lower()

    marcadores = (
        "§",
        "section ",
        "section:",
        "rfc ",
    )

    return any(
        marcador in contexto
        for marcador in marcadores
    )


def _parece_percentual(texto, fim):
    """
    Verifica se a ocorrência é seguida por percentual.

    Exemplos:
        84.9%
        100.0 %
    """

    restante = texto[
        fim:fim + 8
    ]

    return bool(
        re.match(
            r"\s*%",
            restante
        )
    )


def _parece_metrica(texto, fim):
    """
    Identifica números seguidos por unidades de medida.

    Exemplos:
        11.797 ms
        1.234 s
        42.5 MB
    """

    restante = texto[
        fim:fim + 20
    ].lower()

    unidades = (
        "ms",
        "millisecond",
        "milliseconds",
        "sec",
        "secs",
        "second",
        "seconds",
        "kb",
        "mb",
        "gb",
        "kib",
        "mib",
        "gib",
        "kb/s",
        "mb/s",
        "gb/s",
        "hz",
        "khz",
        "mhz",
    )

    for unidade in unidades:
        if re.match(
            rf"\s*{re.escape(unidade)}\b",
            restante
        ):
            return True

    return False


def _parece_score_ou_nota(texto, inicio, fim):
    """
    Identifica números decimais utilizados como score,
    nota ou pontuação.

    Exemplos:
        score: 84.9
        scored 84.9
        rating 7.5
        severity 7.5
        CVSS 7.5
    """

    inicio_contexto = max(0, inicio - 50)
    fim_contexto = min(len(texto), fim + 30)

    contexto = texto[
        inicio_contexto:fim_contexto
    ].lower()

    marcadores = (
        "score",
        "scored",
        "scoring",
        "rating",
        "rated",
        "points",
        "point",
        "grade",
        "severity",
        "cvss",
        "score:",
        "rating:",
        "severity:",
    )

    return any(
        marcador in contexto
        for marcador in marcadores
    )


# ============================================================
# EXTRAÇÃO DE VERSÕES
# ============================================================

def encontrar_versoes(texto):
    """
    Encontra versões de software e filtra falsos positivos.

    São removidos principalmente:
    - IPv4;
    - padrões de rede;
    - seções de RFC;
    - percentuais;
    - métricas;
    - scores/notas;
    - números decimais isolados sem contexto de versão.
    """

    texto = texto_seguro(texto)

    resultados = []

    for match in re.finditer(
        PADRAO_VERSAO,
        texto,
        flags=re.IGNORECASE,
    ):

        valor = match.group(0)

        inicio = match.start()
        fim = match.end()

        # --------------------------------------------------------
        # 1. IPv4
        # --------------------------------------------------------

        if _parece_endereco_ip(valor):
            continue

        # Verifica um trecho maior ao redor da ocorrência
        # para evitar capturar partes de IP.
        trecho = texto[
            max(0, inicio - 20):
            min(len(texto), fim + 20)
        ]

        if re.search(
            PADRAO_IP_COMPLETO,
            trecho,
        ):
            continue

        # --------------------------------------------------------
        # 2. Redes
        # --------------------------------------------------------

        contexto_rede = texto[
            max(0, inicio - 40):
            min(len(texto), fim + 40)
        ]

        if re.search(
            PADRAO_REDE,
            contexto_rede,
            flags=re.IGNORECASE,
        ):
            continue

        if _esta_em_contexto_de_rede(
            texto,
            inicio,
            fim,
        ):
            if not valor.lower().startswith("v"):
                if valor.count(".") <= 2:
                    continue

        # --------------------------------------------------------
        # 3. Seções de RFC
        # --------------------------------------------------------

        if _parece_secao_rfc(
            texto,
            inicio,
        ):
            continue

        # --------------------------------------------------------
        # 4. Percentuais
        # --------------------------------------------------------

        if _parece_percentual(
            texto,
            fim,
        ):
            continue

        # --------------------------------------------------------
        # 5. Métricas
        # --------------------------------------------------------

        if _parece_metrica(
            texto,
            fim,
        ):
            continue

        # --------------------------------------------------------
        # 6. Scores e notas
        # --------------------------------------------------------

        if (
            valor.count(".") == 1
            and _parece_score_ou_nota(
                texto,
                inicio,
                fim,
            )
        ):
            continue

        # --------------------------------------------------------
        # 7. Decimais simples
        # --------------------------------------------------------
        #
        # Exemplo:
        #   0.0
        #   84.9
        #   100.0
        #
        # Só mantemos quando há contexto de versão.
        # --------------------------------------------------------

        if (
            valor.count(".") == 1
            and not valor.lower().startswith("v")
        ):
            if not _contexto_versao(
                texto,
                inicio,
                fim,
            ):
                continue

        # --------------------------------------------------------
        # 8. Evita duplicidades
        # --------------------------------------------------------

        if valor not in resultados:
            resultados.append(valor)

    return resultados


# ============================================================
# OUTROS PADRÕES
# ============================================================

def encontrar_referencias(texto):
    """Encontra referências no formato #123."""

    texto = texto_seguro(texto)

    return list(
        dict.fromkeys(
            re.findall(
                PADRAO_REFERENCIA,
                texto,
            )
        )
    )


def encontrar_erros(texto):
    """Encontra nomes de erros e exceções."""

    texto = texto_seguro(texto)

    return list(
        dict.fromkeys(
            re.findall(
                PADRAO_ERRO,
                texto,
            )
        )
    )


def encontrar_urls(texto):
    """Encontra URLs HTTP e HTTPS."""

    texto = texto_seguro(texto)

    resultados = []

    for url in re.findall(
        PADRAO_URL,
        texto,
    ):

        url = url.rstrip(
            ".,;:!?)]}>"
        )

        if (
            url
            and url not in resultados
        ):
            resultados.append(url)

    return resultados


def encontrar_caminhos(texto):
    """
    Encontra caminhos de arquivos.

    URLs são removidas temporariamente para evitar
    falsos positivos.
    """

    texto = texto_seguro(texto)

    texto_sem_urls = re.sub(
        PADRAO_URL,
        " ",
        texto,
        flags=re.IGNORECASE,
    )

    return list(
        dict.fromkeys(
            re.findall(
                PADRAO_CAMINHO,
                texto_sem_urls,
            )
        )
    )


def encontrar_urgencia(texto):
    """Encontra termos explícitos de urgência."""

    texto = texto_seguro(texto)

    return list(
        dict.fromkeys(
            re.findall(
                PADRAO_URGENCIA,
                texto,
                flags=re.IGNORECASE,
            )
        )
    )


# ============================================================
# ANÁLISE COMPLETA
# ============================================================

def analisar_regex(texto):
    """
    Executa todos os padrões Regex.
    """

    return {
        "versoes": encontrar_versoes(texto),
        "referencias": encontrar_referencias(texto),
        "erros": encontrar_erros(texto),
        "caminhos": encontrar_caminhos(texto),
        "urls": encontrar_urls(texto),
        "urgencia": encontrar_urgencia(texto),
    }


# ============================================================
# LEITURA DO CSV
# ============================================================

def carregar_issues(caminho_csv):
    """Carrega as issues do arquivo CSV."""

    with open(
        caminho_csv,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:

        return list(
            csv.DictReader(arquivo)
        )


def montar_texto_issue(issue):
    """
    Junta título e corpo da issue.
    """

    titulo = texto_seguro(
        issue.get("titulo")
    )

    corpo = texto_seguro(
        issue.get("corpo")
    )

    return f"{titulo}\n{corpo}".strip()


# ============================================================
# PROCESSAMENTO
# ============================================================

def processar_issues(issues):
    """
    Executa a análise Regex em todas as issues.
    """

    resultados = []

    for issue in issues:

        texto = montar_texto_issue(
            issue
        )

        analise = analisar_regex(
            texto
        )

        resultados.append({
            "repositorio": texto_seguro(
                issue.get("repositorio")
            ),
            "numero": texto_seguro(
                issue.get("numero")
            ),
            "titulo": texto_seguro(
                issue.get("titulo")
            ),
            "versoes": "; ".join(
                analise["versoes"]
            ),
            "referencias": "; ".join(
                analise["referencias"]
            ),
            "erros": "; ".join(
                analise["erros"]
            ),
            "caminhos": "; ".join(
                analise["caminhos"]
            ),
            "urls": "; ".join(
                analise["urls"]
            ),
            "urgencia": "; ".join(
                analise["urgencia"]
            ),
        })

    return resultados


# ============================================================
# SALVAR RESULTADOS
# ============================================================

def salvar_resultados(
    resultados,
    caminho_saida,
):
    """
    Salva os resultados em CSV.

    O arquivo é sobrescrito a cada execução para que
    regex_results.csv represente sempre a versão atual
    do Regex.
    """

    caminho_saida = Path(
        caminho_saida
    )

    caminho_saida.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not resultados:
        return

    campos = list(
        resultados[0].keys()
    )

    with open(
        caminho_saida,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
        )

        escritor.writeheader()
        escritor.writerows(
            resultados
        )


# ============================================================
# RESUMO
# ============================================================

def imprimir_resumo(resultados):
    """
    Mostra no terminal a quantidade de issues
    identificadas em cada categoria.
    """

    total = len(resultados)

    print("=" * 55)
    print("DEVISSUES - ANÁLISE REGEX")
    print("=" * 55)

    print(
        f"Total de issues analisadas: {total}"
    )

    print()

    categorias = (
        ("versoes", "Versões"),
        ("referencias", "Referências"),
        ("erros", "Erros/exceções"),
        ("caminhos", "Caminhos de arquivos"),
        ("urls", "URLs"),
        ("urgencia", "Urgência"),
    )

    for campo, nome in categorias:

        quantidade = sum(
            bool(resultado[campo])
            for resultado in resultados
        )

        percentual = (
            quantidade / total * 100
            if total
            else 0
        )

        print(
            f"{nome}: "
            f"{quantidade} issues "
            f"({percentual:.1f}%)"
        )

    print("=" * 55)


# ============================================================
# MAIN
# ============================================================

def main():
    """
    Executa o pipeline completo:
    1. lê issues.csv;
    2. processa Regex;
    3. salva regex_results.csv;
    4. mostra resumo.
    """

    caminho_entrada = Path(
        "dados/issues.csv"
    )

    caminho_saida = Path(
        "resultados/regex_results.csv"
    )

    if not caminho_entrada.exists():

        print(
            f"Arquivo não encontrado: "
            f"{caminho_entrada}"
        )

        return

    issues = carregar_issues(
        caminho_entrada
    )

    resultados = processar_issues(
        issues
    )

    salvar_resultados(
        resultados,
        caminho_saida,
    )

    print(
        f"Issues lidas: "
        f"{len(issues)}"
    )

    print(
        f"Issues processadas: "
        f"{len(resultados)}"
    )

    imprimir_resumo(
        resultados
    )

    print(
        f"Resultados salvos em: "
        f"{caminho_saida}"
    )


if __name__ == "__main__":
    main()