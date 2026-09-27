"""
DevIssues - src/analise.py
Módulo de Análise e Consolidação (Pessoa 3)

Integra a coleta (dados/issues.csv) com os processamentos de Regex (src/regex.py)
e spaCy (src/nlp.py). Responsável por:
1. Classificar issues em Bug, Dívida Técnica, Feature Request e Urgência.
2. Determinar a polaridade do sentimento a partir dos lemas do spaCy.
3. Consolidar e exportar os dados para resultados/relatorio_final.csv.
4. Calcular estatísticas detalhadas para a interface do usuário.
"""

import csv
import os
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.nlp import analisar_texto, carregar_modelos
from src.regex import analisar_regex

# Léxicos para classificação de sentimento baseados em lemas/palavras-chave (Inglês/Português)
LEMAS_POSITIVOS = {
    "thank", "thanks", "great", "awesome", "good", "nice", "resolve", "resolved",
    "fix", "fixed", "help", "helps", "appreciate", "working", "perfect", "obrigado",
    "ótimo", "bom", "resolvido", "ajuda", "funciona"
}

LEMAS_NEGATIVOS = {
    "error", "bug", "fail", "failed", "failure", "broken", "crash", "terrible",
    "bad", "worst", "wrong", "cannot", "unable", "freeze", "slow", "blocking",
    "erro", "falha", "quebrado", "impossível", "lento", "travando"
}


def calcular_sentimento_por_lemmas(lemmas: List[str]) -> str:
    """Classifica a polaridade de sentimento (Positivo, Negativo ou Neutro)

    usando a contagem de lemas encontrados pelo spaCy.
    """
    lemmas_minusculos = [str(lemma).lower() for lemma in lemmas]

    score_pos = sum(1 for l in lemmas_minusculos if l in LEMAS_POSITIVOS)
    score_neg = sum(1 for l in lemmas_minusculos if l in LEMAS_NEGATIVOS)

    if score_pos > score_neg:
        return "Positivo"
    if score_neg > score_pos:
        return "Negativo"
    return "Neutro"


def identificar_categorias(
    issue_dict: Dict[str, Any],
    res_regex: Dict[str, List[str]],
    lemmas: List[str]
) -> Dict[str, bool]:
    """Determina a presença de categorias técnicas combinando labels originais,

    padrões Regex e os lemas extraídos pelo spaCy.
    """
    labels = str(issue_dict.get("labels", "")).lower()
    lemmas_set = {str(l).lower() for l in lemmas}

    # 1. Identificação de Bug
    eh_bug = (
        bool(res_regex.get("erros"))
        or any(b in labels for b in ["bug", "defect", "erro"])
        or bool(lemmas_set.intersection({"bug", "error", "exception", "crash", "fix"}))
    )

    # 2. Identificação de Dívida Técnica
    eh_divida = (
        any(d in labels for d in ["debt", "refactor", "cleanup", "deprecation"])
        or bool(lemmas_set.intersection({"refactor", "clean", "deprecated", "todo", "cleanup"}))
    )

    # 3. Identificação de Feature Request
    eh_feature = (
        any(f in labels for f in ["enhancement", "feature", "request"])
        or bool(lemmas_set.intersection({"feature", "request", "add", "support", "implement", "proposal"}))
    )

    # 4. Identificação de Urgência
    eh_urgente = (
        bool(res_regex.get("urgencia"))
        or any(u in labels for u in ["urgent", "critical", "p0", "p1", "blocker"])
    )

    return {
        "bug": eh_bug,
        "divida_tecnica": eh_divida,
        "feature_request": eh_feature,
        "urgencia": eh_urgente
    }


def carregar_issues_originais(caminho_csv: str = "dados/issues.csv") -> List[Dict[str, Any]]:
    """Lê as issues coletadas do arquivo CSV gerado pela Pessoa 1."""
    if not os.path.exists(caminho_csv):
        return []

    with open(caminho_csv, mode="r", encoding="utf-8") as arq:
        leitor = csv.DictReader(arq)
        return list(leitor)


def processar_e_consolidar_issues(
    issues: List[Dict[str, Any]],
    modelos_nlp: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Aplica o Regex e o spaCy em cada issue e constrói a estrutura consolidada."""
    issues_consolidadas = []

    for issue in issues:
        titulo = issue.get("titulo", "")
        corpo = issue.get("corpo", "")
        texto_completo = f"{titulo}\n{corpo}".strip()

        # Executa a análise Regex (Pessoa 2)
        res_regex = analisar_regex(texto_completo)

        # Executa a análise spaCy (Pessoa 2)
        res_nlp = analisar_texto(texto_completo, modelos_nlp)

        # Processamento exclusivo da Pessoa 3
        lemmas = res_nlp.get("lemmas", [])
        sentimento = calcular_sentimento_por_lemmas(lemmas)
        cats = identificar_categorias(issue, res_regex, lemmas)

        # Monta a linha consolidada
        item_consolidado = {
            "repositorio": issue.get("repositorio", ""),
            "numero": issue.get("numero", ""),
            "titulo": titulo,
            "estado": issue.get("estado", ""),
            "idioma": res_nlp.get("idioma", "en"),
            "bug": "SIM" if cats["bug"] else "NÃO",
            "divida_tecnica": "SIM" if cats["divida_tecnica"] else "NÃO",
            "feature_request": "SIM" if cats["feature_request"] else "NÃO",
            "urgencia": "SIM" if cats["urgencia"] else "NÃO",
            "sentimento": sentimento,
            "erros_encontrados": "; ".join(res_regex.get("erros", [])),
            "versoes_encontradas": "; ".join(res_regex.get("versoes", [])),
            "urgencia_termos": "; ".join(res_regex.get("urgencia", [])),
            "qtd_tokens": len(res_nlp.get("tokens", [])),
            "qtd_entidades": len(res_nlp.get("entidades", [])),
            "url": issue.get("url", "")
        }

        issues_consolidadas.append(item_consolidado)

    return issues_consolidadas


def calcular_estatisticas(issues_consolidadas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Gera o resumo estatístico que será exibido no terminal e na interface."""
    total = len(issues_consolidadas)
    if total == 0:
        return {"total_issues": 0}

    qtd_bug = sum(1 for i in issues_consolidadas if i["bug"] == "SIM")
    qtd_divida = sum(1 for i in issues_consolidadas if i["divida_tecnica"] == "SIM")
    qtd_feature = sum(1 for i in issues_consolidadas if i["feature_request"] == "SIM")
    qtd_urgencia = sum(1 for i in issues_consolidadas if i["urgencia"] == "SIM")

    sentimentos = Counter(i["sentimento"] for i in issues_consolidadas)

    # Extrai os erros e versões mais comuns
    erros_lista = []
    versoes_lista = []
    for i in issues_consolidadas:
        if i["erros_encontrados"]:
            erros_lista.extend([e.strip() for e in i["erros_encontrados"].split(";") if e.strip()])
        if i["versoes_encontradas"]:
            versoes_lista.extend([v.strip() for v in i["versoes_encontradas"].split(";") if v.strip()])

    return {
        "total_issues": total,
        "bug": qtd_bug,
        "divida_tecnica": qtd_divida,
        "feature_request": qtd_feature,
        "urgencia": qtd_urgencia,
        "sentimento": {
            "Positivo": sentimentos.get("Positivo", 0),
            "Neutro": sentimentos.get("Neutro", 0),
            "Negativo": sentimentos.get("Negativo", 0),
        },
        "top_erros": Counter(erros_lista).most_common(5),
        "top_versoes": Counter(versoes_lista).most_common(5),
        "issues_detalhadas": issues_consolidadas
    }


def salvar_relatorio_final(
    issues_consolidadas: List[Dict[str, Any]],
    caminho_saida: str = "resultados/relatorio_final.csv"
) -> None:
    """Salva a base totalmente unificada e processada na pasta resultados."""
    if not issues_consolidadas:
        return

    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    campos = list(issues_consolidadas[0].keys())

    with open(caminho_saida, mode="w", encoding="utf-8-sig", newline="") as arq:
        escritor = csv.DictWriter(arq, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(issues_consolidadas)

    print(f"[OK] Relatório final exportado para: {caminho_saida}")


def executar_analise_completa(caminho_csv: str = "dados/issues.csv") -> Dict[str, Any]:
    """Função principal acionada pela interface ou main.py."""
    print("\n--- INICIANDO ANÁLISE INTEGRADA (PESSOA 3) ---")

    issues = carregar_issues_originais(caminho_csv)
    if not issues:
        print(f"[!] Ficheiro '{caminho_csv}' não encontrado ou vazio.")
        return {}

    print(f"[*] {len(issues)} issues carregadas de '{caminho_csv}'.")
    print("[*] Carregando modelos spaCy...")
    modelos_nlp = carregar_modelos()

    print("[*] Processando Regex, spaCy, Sentimento e Categorização...")
    issues_consolidadas = processar_e_consolidar_issues(issues, modelos_nlp)

    salvar_relatorio_final(issues_consolidadas)
    estatisticas = calcular_estatisticas(issues_consolidadas)

    print("[✓] Análise concluída com sucesso!")
    return estatisticas


if __name__ == "__main__":
    res = executar_analise_completa()
    if res:
        print(f"Total Analisado: {res.get('total_issues')}")
        print(f"Bugs: {res.get('bug')} | Dívida Técnica: {res.get('divida_tecnica')}")