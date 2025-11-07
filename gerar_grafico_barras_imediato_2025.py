#!/usr/bin/env python3
"""
Gera graficos de barras horizontais com os maiores riscos (niveis 4-5)
para o periodo Imediato 2025 em cada dimensao analisada.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List

import matplotlib.pyplot as plt
import numpy as np

from analise_likert_riscos import AnalisadorRiscosLikert

# Configuracao por dimensao
DIMENSIONS: Dict[str, Dict[str, object]] = {
    "Economica": {
        "slug": "economica",
        "friendly": "Riscos Economicos",
        "ylabel": "Variaveis Economicas",
        "output_files": [
            Path("quarto/assets/economicos/grafico_barras_imediato_2025.png"),
            Path("quarto/assets/graficos_agrupados/grafico_barras_economicos_imediato_2025.png"),
        ],
    },
    "Ambiental": {
        "slug": "ambiental",
        "friendly": "Riscos Ambientais",
        "ylabel": "Variaveis Ambientais",
        "output_files": [
            Path("quarto/assets/ambientais/grafico_barras_imediato_2025.png"),
            Path("quarto/assets/graficos_agrupados/grafico_barras_ambientais_imediato_2025.png"),
        ],
    },
    "Geopolitica": {
        "slug": "geopolitica",
        "friendly": "Riscos Geopoliticos",
        "ylabel": "Variaveis Geopoliticas",
        "output_files": [
            Path("quarto/assets/geopoliticos/grafico_barras_imediato_2025.png"),
            Path("quarto/assets/graficos_agrupados/grafico_barras_geopoliticos_imediato_2025.png"),
        ],
    },
    "Tecnologica": {
        "slug": "tecnologica",
        "friendly": "Riscos Tecnologicos",
        "ylabel": "Variaveis Tecnologicas",
        "output_files": [
            Path("quarto/assets/tecnologicos/grafico_barras_imediato_2025.png"),
            Path("quarto/assets/graficos_agrupados/grafico_barras_tecnologicos_imediato_2025.png"),
        ],
    },
    "Social": {
        "slug": "social",
        "friendly": "Riscos Sociais",
        "ylabel": "Variaveis Sociais",
        "output_files": [
            Path("quarto/assets/social/grafico_barras_imediato_2025.png"),
            Path("quarto/assets/graficos_agrupados/grafico_barras_social_imediato_2025.png"),
            # Caminho original utilizado no livro (mantido por compatibilidade)
            Path("quarto/assets/graficos_agrupados/grafico_barras_imediato_2025.png"),
        ],
        # Ajustes especificos para nomes longos frequentes na dimensao social
        "abreviacoes": {
            "Insuficiencia de servicos publicos essenciais, como saude, saneamento, transporte, seguranca e educacao, que impacta diretamente a qualidade de vida da populacao e a forca de trabalho vinculada ao setor portuario": "Insuficiencia de servicos publicos essenciais",
            "Acidentes rodoviarios e ferroviarios de alta severidade em areas proximas aos portos": "Acidentes rodoviarios e ferroviarios de alta severidade",
            "Falta de recursos humanos capacitados e especializados no setor portuario": "Falta de recursos humanos capacitados e especializados",
            "Desigualdades raciais/etnicas e de genero": "Desigualdades raciais/etnicas e de genero",
            "Ausencia do Estado junto as populacoes proximas aos portos": "Ausencia do Estado junto as populacoes portuarias",
        },
    },
}

PERIODO_TARGET = "imediato_2025"


def ascii_safe(texto: str) -> str:
    """Remove acentuacao para evitar erros em consoles Windows."""
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )


def selecionar_dimensoes(argumentos: Iterable[str]) -> List[str]:
    """Seleciona as dimensoes a processar a partir dos argumentos de linha de comando."""
    if not argumentos:
        return list(DIMENSIONS.keys())

    selecionadas: List[str] = []
    slug_map = {cfg["slug"]: chave for chave, cfg in DIMENSIONS.items()}

    for argumento in argumentos:
        chave = argumento.strip().lower()
        if chave in ("all", "todas"):
            return list(DIMENSIONS.keys())

        if chave in slug_map:
            selecionadas.append(slug_map[chave])
        else:
            # tentativa direta com o nome da chave
            for nome_dimensao in DIMENSIONS:
                if nome_dimensao.lower() == chave:
                    selecionadas.append(nome_dimensao)
                    break
            else:
                print(f"Aviso: dimensao desconhecida ignorada -> {argumento}")

    # remove duplicados preservando ordem
    return list(dict.fromkeys(selecionadas))


def gerar_grafico_barras_imediato(
    analisador: AnalisadorRiscosLikert,
    mapeamento: Dict[str, Dict[str, List[str]]],
    dimensao: str,
) -> Path | None:
    """Cria o grafico horizontal para a dimensao informada."""
    config = DIMENSIONS[dimensao]
    friendly = config["friendly"]
    ylabel = config["ylabel"]
    arquivos_saida: List[Path] = config["output_files"]  # type: ignore[assignment]
    abreviacoes: Dict[str, str] = config.get("abreviacoes", {})  # type: ignore[assignment]

    print(f"\nGerando grafico de barras - {ascii_safe(friendly)}...")

    dados_dimensao = mapeamento.get(dimensao, {})
    variaveis_periodo = dados_dimensao.get(PERIODO_TARGET, [])

    if not variaveis_periodo:
        print("  Nenhum dado encontrado para o periodo alvo. Grafico nao gerado.")
        return None

    percentuais_risco_alto: Dict[str, float] = {}

    for variavel in variaveis_periodo:
        if variavel not in analisador.dados_brutos:
            continue

        serie = analisador.dados_brutos[variavel]
        estatisticas = analisador.analisar_frequencias_likert(serie)
        if not estatisticas:
            continue

        label_completo = analisador.gerar_label_sucinto(variavel, incluir_numero=False)
        label_ascii = ascii_safe(label_completo)
        label_abreviado = abreviacoes.get(label_ascii, label_ascii)
        percentuais_risco_alto[label_abreviado] = estatisticas["percentual_risco_alto"]

    if not percentuais_risco_alto:
        print("  Nenhuma variavel valida encontrada. Grafico nao gerado.")
        return None

    # Ordena por percentual (maior no topo) e prepara dados
    ordenados_desc = sorted(percentuais_risco_alto.items(), key=lambda item: item[1], reverse=True)
    labels = [item[0] for item in ordenados_desc][::-1]
    valores = np.array([item[1] for item in ordenados_desc][::-1])

    altura = max(6.0, 0.45 * len(labels))
    plt.figure(figsize=(14, altura))

    # Gera paleta baseada na intensidade
    amplitude = float(np.ptp(valores))
    if amplitude == 0:  # evita divisao por zero quando todos sao iguais
        cores = ["#FF8C00"] * len(valores)
    else:
        norm = (valores - valores.min()) / amplitude
        cmap = plt.colormaps["OrRd"]
        cores = [cmap(0.35 + 0.5 * valor) for valor in norm]

    barras = plt.barh(range(len(labels)), valores, color=cores, edgecolor="black", linewidth=0.5)

    plt.xlabel("Percentual de respostas em niveis altos (4-5)", fontsize=12, fontweight="bold")
    plt.ylabel(ylabel, fontsize=12, fontweight="bold")
    plt.title(
        f"{friendly} - Imediato 2025\nPercentual de respostas em niveis altos (4-5)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    plt.yticks(range(len(labels)), labels, fontsize=10)
    plt.xlim(0, max(valores) * 1.1)
    plt.xticks(fontsize=10)
    plt.grid(axis="x", alpha=0.3, linestyle="--")

    for barra, valor in zip(barras, valores):
        plt.text(
            barra.get_width() + 0.5,
            barra.get_y() + barra.get_height() / 2,
            f"{valor:.1f}%",
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()

    destino_principal = arquivos_saida[0]
    destino_principal.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(destino_principal, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

    # Copia para caminhos adicionais (quando existirem)
    for destino_extra in arquivos_saida[1:]:
        destino_extra.parent.mkdir(parents=True, exist_ok=True)
        destino_extra.write_bytes(destino_principal.read_bytes())

    print(
        f"  Grafico salvo em: {destino_principal} "
        f"(copiado para {len(arquivos_saida) - 1} caminhos adicionais)"
    )
    print(f"  Total de variaveis analisadas: {len(labels)}")
    print(f"  Maior risco: {valores.max():.1f}% ({ascii_safe(labels[-1])})")
    print(f"  Menor risco: {valores.min():.1f}% ({ascii_safe(labels[0])})")
    print(f"  Media geral de risco alto: {valores.mean():.1f}%")
    print("  Top 3 riscos imediatos:")
    for nome, valor in ordenados_desc[:3]:
        print(f"    - {ascii_safe(nome)}: {valor:.1f}%")

    return destino_principal


def gerar_grafico_barras_imediato_2025() -> Path | None:
    """
    Funcao mantida por compatibilidade com scripts antigos.
    Continua gerando o grafico para a dimensao Social.
    """
    analisador = AnalisadorRiscosLikert()
    analisador.carregar_dados()
    mapeamento = analisador.mapear_variaveis_por_dimensao()
    return gerar_grafico_barras_imediato(analisador, mapeamento, "Social")


def main() -> None:
    dimensoes = selecionar_dimensoes(sys.argv[1:])
    if not dimensoes:
        print("Nenhuma dimensao valida informada. Encerrando.")
        return

    analisador = AnalisadorRiscosLikert()
    analisador.carregar_dados()
    mapeamento = analisador.mapear_variaveis_por_dimensao()

    for dimensao in dimensoes:
        gerar_grafico_barras_imediato(analisador, mapeamento, dimensao)


if __name__ == "__main__":
    main()
