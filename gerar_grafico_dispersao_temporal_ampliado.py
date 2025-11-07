#!/usr/bin/env python3
"""
Gera o grafico de dispersao temporal ampliado utilizando todas as variaveis disponiveis,
com distribuicao de pontos sem sobreposicao e analises estatisticas detalhadas.
"""

from __future__ import annotations

import math
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from matplotlib.lines import Line2D

from analise_likert_riscos import AnalisadorRiscosLikert

# Cores por dimensao
CORES_DIMENSAO = {
    "Economica": "#2E86AB",  # Azul
    "Ambiental": "#228B22",  # Verde
    "Geopolitica": "#A23B72",  # Roxo
    "Social": "#F18F01",  # Laranja
    "Tecnologica": "#DC143C",  # Vermelho
}

# Nomes amigaveis (sem acentos para evitar problemas de codificacao)
NOMES_DIMENSAO = {
    "Economica": "Economica",
    "Ambiental": "Ambiental",
    "Geopolitica": "Geopolitica",
    "Social": "Social",
    "Tecnologica": "Tecnologica",
}

# Paleta por quadrante (cores mais saturadas para os pontos)
CORES_QUADRANTE = {
    "Q1": "#D73027",  # Vermelho
    "Q2": "#F4A259",  # Laranja
    "Q3": "#1B9E77",  # Verde
    "Q4": "#4575B4",  # Azul
}

# --------------------------------------------------------------------------- #
# Utilitarios
# --------------------------------------------------------------------------- #

def ascii_safe(texto: str) -> str:
    """Remove acentos para evitar problemas em terminais Windows."""
    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )


def resumir_label_grafico(texto: str, limite: int = 35) -> str:
    """Limita o label a um numero maximo de caracteres preservando palavras-chave."""
    texto = " ".join(texto.split())
    if len(texto) <= limite:
        return texto

    palavras = texto.split()
    selecionadas: List[str] = []
    for palavra in palavras:
        candidato = " ".join(selecionadas + [palavra])
        if len(candidato) <= limite - 3:
            selecionadas.append(palavra)
            continue

        if palavra.lower() in {"risco", "impacto", "crise", "piora", "aumento", "mudancas"}:
            selecionadas.append(palavra)

        if len(candidato) > limite - 3:
            break

    if not selecionadas:
        selecionadas = palavras[:max(1, min(3, len(palavras)))]

    return " ".join(selecionadas)[: limite - 3].rstrip() + "..."


def gerar_labels_variavel(
    analisador: AnalisadorRiscosLikert, nome_variavel: str
) -> Tuple[str, str]:
    """Retorna (label_grafico, label_texto) para a variavel informada."""
    label_base = analisador.gerar_label_sucinto(nome_variavel, incluir_numero=False)
    label_texto = analisador.gerar_label_sucinto(nome_variavel, incluir_numero=True)

    label_grafico = resumir_label_grafico(label_base)

    return ascii_safe(label_grafico), ascii_safe(label_texto)


def classificar_tendencia(delta_temporal: float) -> str:
    """Classifica a variacao temporal com base no sinal e na magnitude."""
    if delta_temporal >= 0.5:
        return "Piora significativa"
    if delta_temporal >= 0.2:
        return "Piora moderada"
    if delta_temporal <= -0.5:
        return "Melhora significativa"
    if delta_temporal <= -0.2:
        return "Melhora moderada"
    if abs(delta_temporal) > 0.05:
        return "Alteracao leve"
    return "Estavel"


# --------------------------------------------------------------------------- #
# Preparacao de dados
# --------------------------------------------------------------------------- #

def coletar_pares_variaveis(
    analisador: AnalisadorRiscosLikert,
) -> List[Dict]:
    """Gera a lista de pares (curto x longo prazo) para todas as dimensoes."""
    mapeamento = analisador.mapear_variaveis_por_dimensao()
    pares_variaveis: List[Dict] = []

    for dimensao, periodos in mapeamento.items():
        print(f"\n-- Processando dimensao: {ascii_safe(dimensao)}")
        variaveis_curto = periodos.get("curto_prazo_2026_2027", [])
        variaveis_longo = periodos.get("longo_prazo_2035", [])

        if not variaveis_curto or not variaveis_longo:
            print("   Nenhum par encontrado para os periodos requeridos.")
            continue

        indice_longo: Dict[str, List[str]] = defaultdict(list)
        for var_longo in variaveis_longo:
            match = re.match(r"^(\d+\.\d+)", var_longo)
            if match:
                indice_longo[match.group(1)].append(var_longo)

        for var_curto in variaveis_curto:
            match = re.match(r"^(\d+\.\d+)", var_curto)
            if not match:
                continue

            num_base = match.group(1)
            candidatos = indice_longo.get(num_base)
            if not candidatos:
                continue

            var_longo = candidatos[0]
            if (
                var_curto not in analisador.dados_brutos
                or var_longo not in analisador.dados_brutos
            ):
                continue

            stats_curto = analisador.analisar_frequencias_likert(
                analisador.dados_brutos[var_curto]
            )
            stats_longo = analisador.analisar_frequencias_likert(
                analisador.dados_brutos[var_longo]
            )

            if not stats_curto or not stats_longo:
                continue

            label_grafico, label_texto = gerar_labels_variavel(analisador, var_curto)

            pares_variaveis.append(
                {
                    "variavel": var_curto,
                    "label_grafico": label_grafico,
                    "label_texto": label_texto,
                    "dimensao": dimensao,
                    "nome_dimensao": NOMES_DIMENSAO.get(dimensao, dimensao),
                    "cor": CORES_DIMENSAO[dimensao],
                    "stats_curto": stats_curto,
                    "stats_longo": stats_longo,
                }
            )

    print(f"\nTotal de pares mapeados: {len(pares_variaveis)}")
    return pares_variaveis


def preparar_dados_completos(dados_pares: List[Dict]) -> List[Dict]:
    """Calcula metricas adicionais para cada par de variavel."""
    print("== Preparando analise completa de dispersao temporal ==")

    dados_preparados: List[Dict] = []
    for par in dados_pares:
        stats_curto = par["stats_curto"]
        stats_longo = par["stats_longo"]

        mediana_combinada = (stats_curto["mediana"] + stats_longo["mediana"]) / 2
        delta_temporal = stats_longo["mediana"] - stats_curto["mediana"]
        delta_absoluto = abs(delta_temporal)
        variabilidade_media = (stats_curto["iqr"] + stats_longo["iqr"]) / 2

        dados_preparados.append(
            {
                **par,
                "mediana_combinada": mediana_combinada,
                "delta_temporal": delta_temporal,
                "delta_absoluto": delta_absoluto,
                "variabilidade_media": variabilidade_media,
                "tendencia": classificar_tendencia(delta_temporal),
            }
        )

    print(f"Total de variaveis consideradas: {len(dados_preparados)}")
    return dados_preparados


def distribuir_pontos_sem_superposicao(
    dados: List[Dict], raio_base: float = 0.18
) -> Dict[Tuple[float, float], List[Dict]]:
    """
    Distribui os pontos ao redor da coordenada original para evitar sobreposicao.
    Aumenta o raio base e usa distribuição otimizada para melhor espaçamento.

    Retorna um dicionario com os clusters originais (coordenada base -> lista de itens).
    """
    clusters: Dict[Tuple[float, float], List[Dict]] = defaultdict(list)

    for item in dados:
        chave = (
            round(item["stats_curto"]["mediana"], 4),
            round(item["stats_longo"]["mediana"], 4),
        )
        clusters[chave].append(item)

    for (base_x, base_y), elementos in clusters.items():
        n = len(elementos)

        if n == 1:
            elementos[0]["scatter_x"] = base_x
            elementos[0]["scatter_y"] = base_y
            elementos[0]["cluster_tamanho"] = 1
            continue

        # Aumenta o raio base para melhor separação visual
        raio = min(0.45, raio_base + (n - 1) * 0.04)
        
        # Usa espiral para melhor distribuição quando há muitos pontos
        if n <= 6:
            angulos = np.linspace(0, 2 * np.pi, n, endpoint=False)
        else:
            # Distribuição em espiral para muitos pontos
            angulos = []
            for i in range(n):
                angulo = (i * 2 * np.pi / n) + (i * 0.3)  # Adiciona rotação progressiva
                angulos.append(angulo)

        for i, elemento in enumerate(elementos):
            if i < len(angulos):
                angulo = angulos[i]
            else:
                angulo = (i * 2 * np.pi / n)
            
            # Varia o raio ligeiramente para criar mais separação
            raio_variado = raio * (0.8 + 0.4 * (i / n))
            
            desloc_x = raio_variado * math.cos(angulo)
            desloc_y = raio_variado * math.sin(angulo)
            scatter_x = base_x + desloc_x
            scatter_y = base_y + desloc_y

            # Garante que o ponto permaneça dentro da escala Likert com margem
            elemento["scatter_x"] = float(np.clip(scatter_x, 1.2, 4.8))
            elemento["scatter_y"] = float(np.clip(scatter_y, 1.2, 4.8))
            elemento["cluster_tamanho"] = n

    return clusters


def gerar_resumo_quadrantes(
    dados: List[Dict], limiar_x: float, limiar_y: float
) -> Dict[str, List[Dict]]:
    """Organiza os itens por quadrante com base nos limiares informados."""
    quadrantes = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}

    for item in dados:
        x_mediana = item["stats_curto"]["mediana"]
        y_mediana = item["stats_longo"]["mediana"]

        if x_mediana >= limiar_x and y_mediana >= limiar_y:
            item["quadrante"] = "Q1"
            quadrantes["Q1"].append(item)
        elif x_mediana < limiar_x and y_mediana >= limiar_y:
            item["quadrante"] = "Q2"
            quadrantes["Q2"].append(item)
        elif x_mediana < limiar_x and y_mediana < limiar_y:
            item["quadrante"] = "Q3"
            quadrantes["Q3"].append(item)
        else:  # x_mediana >= limiar_x and y_mediana < limiar_y
            item["quadrante"] = "Q4"
            quadrantes["Q4"].append(item)

    return quadrantes


def selecionar_pontos_para_rotular(
    dados: List[Dict],
    limiar_x: float,
    limiar_y: float,
    max_por_quadrante: int = 6,
    limite_total: int = 30,
) -> List[Dict]:
    """Seleciona um conjunto equilibrado de pontos para rotulagem com mais rótulos e melhor distribuição."""
    quadrantes = gerar_resumo_quadrantes(dados, limiar_x, limiar_y)
    selecionados: List[Dict] = []

    # Critérios de seleção mais refinados por quadrante
    ordenadores = {
        "Q1": lambda item: (
            (item["stats_curto"]["mediana"] + item["stats_longo"]["mediana"]) / 2,  # Média mais alta
            item["variabilidade_media"],  # Maior variabilidade
            item.get("cluster_tamanho", 1),  # Maiores clusters
        ),
        "Q2": lambda item: (
            item["delta_temporal"],  # Maior piora
            item["variabilidade_media"],  # Maior variabilidade
            item.get("cluster_tamanho", 1),  # Maiores clusters
        ),
        "Q3": lambda item: (
            -item["delta_absoluto"],  # Menor mudança (mais estáveis)
            item["variabilidade_media"],  # Maior variabilidade
            item.get("cluster_tamanho", 1),  # Maiores clusters
        ),
        "Q4": lambda item: (
            -item["delta_temporal"],  # Maior melhoria
            item["variabilidade_media"],  # Maior variabilidade
            item.get("cluster_tamanho", 1),  # Maiores clusters
        ),
    }

    # Seleção balanceada por quadrante
    for nome_quadrante, itens in quadrantes.items():
        if not itens:
            continue
            
        # Ordena por múltiplos critérios
        itens_ordenados = sorted(
            itens,
            key=ordenadores[nome_quadrante],
            reverse=True,
        )
        
        # Seleciona mais pontos em quadrantes mais populosos
        ajuste_max = max_por_quadrante
        if len(itens) > 15:  # Quadrantes muito densos ganham mais rótulos
            ajuste_max = max_por_quadrante + 2
        elif len(itens) < 5:  # Quadrantes esparsos ganham menos
            ajuste_max = max(2, max_por_quadrante - 2)
            
        selecionados.extend(itens_ordenados[:ajuste_max])

    # Se ainda tiver espaço, adiciona pontos importantes restantes
    if len(selecionados) < limite_total:
        restantes = [
            item for item in dados if item not in selecionados
        ]
        
        # Prioriza clusters grandes e alta variabilidade
        restantes_ordenados = sorted(
            restantes,
            key=lambda item: (
                item.get("cluster_tamanho", 1) * 2,  # Dobra peso para clusters
                item["variabilidade_media"] * 1.5,  # 1.5x peso para variabilidade
                item["delta_absoluto"],  # Mudanças temporais
            ),
            reverse=True,
        )

        faltam = min(limite_total - len(selecionados), len(restantes_ordenados))
        selecionados.extend(restantes_ordenados[:faltam])

    return selecionados[:limite_total]


# --------------------------------------------------------------------------- #
# Visualizacao
# --------------------------------------------------------------------------- #

def gerar_grafico_dispersao_temporal_ampliado() -> Optional[Path]:
    """Gera o grafico de dispersao temporal ampliado."""
    print("=== GERANDO GRAFICO DE DISPERSAO TEMPORAL AMPLIADO ===")

    analisador = AnalisadorRiscosLikert()
    analisador.carregar_dados()

    pares_variaveis = coletar_pares_variaveis(analisador)
    if not pares_variaveis:
        print("Nenhum par de variaveis encontrado para a analise.")
        return None

    dados_completos = preparar_dados_completos(pares_variaveis)
    clusters = distribuir_pontos_sem_superposicao(dados_completos)

    limiar_x = 3.0
    limiar_y = 3.0
    resumo_quadrantes = gerar_resumo_quadrantes(dados_completos, limiar_x, limiar_y)

    x_vals = [item["scatter_x"] for item in dados_completos]
    y_vals = [item["scatter_y"] for item in dados_completos]
    cores = [CORES_QUADRANTE[item["quadrante"]] for item in dados_completos]
    tamanhos = [
        30 + item["variabilidade_media"] * 50 + (item.get("cluster_tamanho", 1) - 1) * 10
        for item in dados_completos
    ]

    sns.set_style("whitegrid")
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(16, 12))

    scatter = ax.scatter(
        x_vals,
        y_vals,
        c=cores,
        s=tamanhos,
        alpha=0.82,
        edgecolors="black",
        linewidth=1.1,
    )

    # Linhas de referencia
    ax.plot([1, 5], [1, 5], "k--", alpha=0.6, linewidth=2.0, label="Riscos estaveis (y=x)")
    ax.axvline(
        x=limiar_x,
        color="#FF8C00",
        linestyle="--",
        alpha=0.6,
        linewidth=2,
        label="Limiar neutro (3.0)",
    )
    ax.axhline(y=limiar_y, color="#FF8C00", linestyle="--", alpha=0.6, linewidth=2)

    ax.set_xlabel(
        "Mediana Curto Prazo (2026-2027)\nPercepcao de risco imediata",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_ylabel(
        "Mediana Longo Prazo (ate 2035)\nPercepcao de risco estrategica",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_title(
        "Analise de Dispersao Temporal de Riscos Portuarios\n"
        f"{len(dados_completos)} variaveis avaliadas entre horizontes de curto e longo prazo",
        fontsize=18,
        fontweight="bold",
        pad=30,
    )

    ax.set_xlim(1.4, 5.6)
    ax.set_ylim(1.4, 5.6)
    ax.set_xticks(np.arange(2, 6))
    ax.set_yticks(np.arange(2, 6))
    ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

    fig.subplots_adjust(left=0.22, right=0.78, top=0.9, bottom=0.2)

    # Anotacoes de clusters (exibe multiplicadores quando ha sobreposicao)
    for (base_x, base_y), itens in clusters.items():
        if len(itens) <= 1:
            continue
        ax.text(
            base_x,
            base_y,
            f"{len(itens)} pts",
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="#333333",
        )

    # Seleciona rotulos equilibrados por quadrante
    itens_rotulados = selecionar_pontos_para_rotular(dados_completos, limiar_x, limiar_y)
    
    # Configuração expandida de offsets para melhor espaçamento - DISTÂNCIA AUMENTADA
    offset_config = {
        "Q1": [
            (60, 45), (-65, 48), (55, -35), (-58, -32), (45, 55), (-50, 55),
            (70, 25), (-72, 25), (48, -50), (-48, -50), (60, 0), (-60, 0),
            (40, 65), (-45, 65), (65, -25), (-65, -25)
        ],
        "Q2": [
            (58, 48), (62, -38), (45, 60), (52, -55), (38, 65), (65, 20),
            (35, -60), (75, 40), (40, 0), (58, -25), (48, 35), (55, -45),
            (42, 70), (-60, 45), (68, -30)
        ],
        "Q3": [
            (-60, -48), (55, -48), (-52, -58), (48, -65), (-45, -55), (58, -40),
            (-58, -35), (52, -35), (-40, -65), (55, -25), (-48, -40), (45, -55),
            (-55, -45), (50, -50), (-42, -60)
        ],
        "Q4": [
            (-60, 45), (-58, -40), (-48, 55), (-52, -55), (-42, 65), (-65, 25),
            (-45, -60), (-68, 40), (-55, 0), (-58, -25), (-48, 35), (-62, -45),
            (-40, 70), (-55, -50), (-65, -30)
        ],
    }
    default_offsets = [
        (55, 40), (-55, 40), (55, -40), (-55, -40),
        (65, 25), (-65, 25), (65, -25), (-65, -25),
        (45, 55), (-45, 55), (45, -55), (-45, -55),
        (60, 30), (-60, 30), (60, -30), (-60, -30)
    ]
    offsets_usados: Dict[str, int] = defaultdict(int)

    for item in itens_rotulados:
        x_pos = item["scatter_x"]
        y_pos = item["scatter_y"]

        quadrante = item.get("quadrante")
        if not quadrante:
            if x_pos >= limiar_x and y_pos >= limiar_y:
                quadrante = "Q1"
            elif x_pos < limiar_x and y_pos >= limiar_y:
                quadrante = "Q2"
            elif x_pos < limiar_x and y_pos < limiar_y:
                quadrante = "Q3"
            else:
                quadrante = "Q4"
            item["quadrante"] = quadrante

        offsets = offset_config.get(quadrante, default_offsets)
        offset = offsets[offsets_usados[quadrante] % len(offsets)]
        offsets_usados[quadrante] += 1

        ha = "left" if offset[0] >= 0 else "right"
        va = "bottom" if offset[1] >= 0 else "top"

        # Ajuste fino baseado na posição para evitar bordas
        if x_pos + offset[0]/100 > 4.8:  # Próximo da borda direita
            offset = (-abs(offset[0]), offset[1])
            ha = "right"
        elif x_pos + offset[0]/100 < 1.2:  # Próximo da borda esquerda
            offset = (abs(offset[0]), offset[1])
            ha = "left"
            
        if y_pos + offset[1]/100 > 4.8:  # Próximo da borda superior
            offset = (offset[0], -abs(offset[1]))
            va = "top"
        elif y_pos + offset[1]/100 < 1.2:  # Próximo da borda inferior
            offset = (offset[0], abs(offset[1]))
            va = "bottom"

        ax.annotate(
            item["label_grafico"],
            (x_pos, y_pos),
            xytext=offset,
            textcoords="offset points",
            fontsize=8.5,  # Fonte ligeiramente menor para caber mais rótulos
            ha=ha,
            va=va,
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="white",
                alpha=0.94,
                edgecolor="#555555",
                linewidth=0.8,
            ),
            arrowprops=dict(
                arrowstyle="->",
                connectionstyle="arc3,rad=0.08",
                color="#666666",
                alpha=0.7,
                linewidth=0.8,
            ),
        )

    # Legenda por quadrante
    descricoes_quadrantes = {
        "Q1": "Riscos cronicos",
        "Q2": "Riscos emergentes",
        "Q3": "Riscos controlados",
        "Q4": "Riscos em melhoria",
    }
    handles_quadrantes = []
    for codigo in ("Q1", "Q2", "Q3", "Q4"):
        quantidade = len(resumo_quadrantes[codigo])
        handles_quadrantes.append(
            Line2D(
                [],
                [],
                marker="o",
                linestyle="",
                markerfacecolor=CORES_QUADRANTE[codigo],
                markeredgecolor="black",
                markersize=9,
                label=f"{codigo} - {descricoes_quadrantes[codigo]} ({quantidade})",
            )
        )

    legenda_quadrantes = ax.legend(
        handles=handles_quadrantes,
        loc="upper left",
        bbox_to_anchor=(1.02, 0.78),
        framealpha=0.95,
        fontsize=11,
        title="Quadrantes",
        title_fontsize=12,
    )
    ax.add_artist(legenda_quadrantes)

    handles_referencias = [
        Line2D([], [], color="k", linestyle="--", linewidth=2, label="Riscos estaveis (y=x)"),
        Line2D([], [], color="#FF8C00", linestyle="--", linewidth=2, label="Limiar neutro (3.0)"),
    ]
    ax.legend(
        handles=handles_referencias,
        loc="upper left",
        bbox_to_anchor=(1.02, 0.45),
        framealpha=0.95,
        fontsize=10,
    )

    # Quadros explicativos posicionados fora do grafico
    caixa_quadrante = dict(boxstyle="round,pad=0.4", alpha=0.85, linewidth=1.0)
    ax.text(
        -0.24,
        1.02,
        "Q1 - Riscos cronicos\n(alto x alto)",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="top",
        ha="left",
        bbox={**caixa_quadrante, "facecolor": CORES_QUADRANTE["Q1"]},
    )
    ax.text(
        1.02,
        1.02,
        "Q2 - Riscos emergentes\n(baixo x alto)",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="top",
        ha="left",
        bbox={**caixa_quadrante, "facecolor": CORES_QUADRANTE["Q2"]},
    )
    ax.text(
        -0.24,
        -0.08,
        "Q3 - Riscos controlados\n(baixo x baixo)",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="bottom",
        ha="left",
        bbox={**caixa_quadrante, "facecolor": CORES_QUADRANTE["Q3"]},
    )
    ax.text(
        1.02,
        -0.08,
        "Q4 - Riscos em melhoria\n(alto x baixo)",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="bottom",
        ha="left",
        bbox={**caixa_quadrante, "facecolor": CORES_QUADRANTE["Q4"]},
    )

    total_vars = len(dados_completos)
    estatisticas_quadrantes = []
    for codigo, descricao in [
        ("Q1", "Riscos cronicos"),
        ("Q2", "Riscos emergentes"),
        ("Q3", "Riscos controlados"),
        ("Q4", "Riscos em melhoria"),
    ]:
        quantidade = len(resumo_quadrantes[codigo])
        percentual = (quantidade / total_vars) * 100 if total_vars else 0
        estatisticas_quadrantes.append(f"{descricao}: {quantidade} ({percentual:.1f}%)")

    fig.text(
        0.5,
        0.07,
        " | ".join(estatisticas_quadrantes),
        fontsize=11,
        ha="center",
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#EFEFEF", alpha=0.95),
    )

    caminho_saida = Path("quarto/assets/graficos_agrupados/grafico_dispersao_temporal_riscos_ampliado.png")
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(caminho_saida, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

    print(f"\n>> Grafico salvo em: {caminho_saida}")

    gerar_analise_estatistica_ampliada(dados_completos, resumo_quadrantes, limiar_x, limiar_y)
    return caminho_saida


# --------------------------------------------------------------------------- #
# Analise descritiva
# --------------------------------------------------------------------------- #

def gerar_analise_estatistica_ampliada(
    dados_completos: List[Dict],
    resumo_quadrantes: Dict[str, List[Dict]],
    limiar_x: float,
    limiar_y: float,
) -> None:
    """Imprime estatisticas e insights detalhados sobre a dispersao temporal."""
    print("\n" + "=" * 86)
    print("ANALISE ESTATISTICA COMPLETA - DISPERSAO TEMPORAL DE RISCOS")
    print("=" * 86)

    x_vals = [item["stats_curto"]["mediana"] for item in dados_completos]
    y_vals = [item["stats_longo"]["mediana"] for item in dados_completos]
    deltas = [item["delta_temporal"] for item in dados_completos]
    deltas_abs = [item["delta_absoluto"] for item in dados_completos]

    print("\n-- Estatisticas gerais")
    print(f"Total de variaveis analisadas: {len(dados_completos)}")
    print(f"Mediana curto prazo - media: {np.mean(x_vals):.2f} | desvio: {np.std(x_vals):.2f}")
    print(f"Mediana longo prazo - media: {np.mean(y_vals):.2f} | desvio: {np.std(y_vals):.2f}")
    print(f"Delta temporal medio: {np.mean(deltas):.2f}")
    print(f"Variacao absoluta media: {np.mean(deltas_abs):.2f}")

    correlacao = np.corrcoef(x_vals, y_vals)[0, 1] if len(dados_completos) > 1 else float("nan")
    print(f"Correlacao de Pearson (curto x longo prazo): {correlacao:.3f}")
    if correlacao > 0.7:
        print("Interpretacao: padrao altamente persistente (riscos tendem a se manter elevados)")
    elif correlacao > 0.4:
        print("Interpretacao: correlacao positiva moderada (pouca mudanca de hierarquia de riscos)")
    elif correlacao > 0.1:
        print("Interpretacao: correlacao fraca (espaco para mudancas relevantes)")
    else:
        print("Interpretacao: correlacao muito fraca (riscos com trajetorias divergentes)")

    print("\n-- Analise por dimensao")
    print("-" * 50)
    por_dimensao: Dict[str, List[Dict]] = defaultdict(list)
    for item in dados_completos:
        por_dimensao[item["dimensao"]].append(item)

    for dimensao, itens in sorted(por_dimensao.items()):
        medias_curto = np.mean([i["stats_curto"]["mediana"] for i in itens])
        medias_longo = np.mean([i["stats_longo"]["mediana"] for i in itens])
        media_delta = np.mean([i["delta_temporal"] for i in itens])
        media_abs = np.mean([i["delta_absoluto"] for i in itens])

        print(f"{NOMES_DIMENSAO[dimensao]} ({len(itens)} variaveis)")
        print(f"  Mediana curto prazo avg: {medias_curto:.2f}")
        print(f"  Mediana longo prazo avg: {medias_longo:.2f}")
        print(f"  Delta medio: {media_delta:.2f}")
        print(f"  Variacao absoluta media: {media_abs:.2f}")
        print(f"  Tendencia predominante: {classificar_tendencia(media_delta)}")

        top_variabilidade = sorted(
            itens,
            key=lambda item: item["variabilidade_media"],
            reverse=True,
        )[:3]
        print("  Top 3 variaveis por variabilidade:")
        for idx, item in enumerate(top_variabilidade, start=1):
            print(
                f"    {idx}. {item['label_texto']} (delta={item['delta_temporal']:.2f}, "
                f"IQR medio={item['variabilidade_media']:.2f})"
            )
        print()

    print("-- Analise por quadrante (limiar 3.0)")
    print("-" * 50)
    descricoes_quadrante = {
        "Q1": "Riscos cronicos (alto x alto)",
        "Q2": "Riscos emergentes (baixo x alto)",
        "Q3": "Riscos controlados (baixo x baixo)",
        "Q4": "Riscos em melhoria (alto x baixo)",
    }

    for codigo in ("Q1", "Q2", "Q3", "Q4"):
        itens = resumo_quadrantes[codigo]
        percentual = (len(itens) / len(dados_completos) * 100) if dados_completos else 0
        print(f"{descricoes_quadrante[codigo]}: {len(itens)} variaveis ({percentual:.1f}%)")

        if not itens:
            continue

        if codigo == "Q1":
            destaque = sorted(
                itens,
                key=lambda item: (item["stats_curto"]["mediana"] + item["stats_longo"]["mediana"]) / 2,
                reverse=True,
            )[:5]
        elif codigo == "Q2":
            destaque = sorted(
                itens,
                key=lambda item: item["delta_temporal"],
                reverse=True,
            )[:5]
        elif codigo == "Q3":
            destaque = sorted(
                itens,
                key=lambda item: item["delta_absoluto"],
            )[:5]
        else:  # Q4
            destaque = sorted(
                itens,
                key=lambda item: item["delta_temporal"],
            )[:5]

        for idx, item in enumerate(destaque, start=1):
            print(
                f"  {idx}. {item['label_texto']} ({item['nome_dimensao']}) - "
                f"curto={item['stats_curto']['mediana']:.2f} | "
                f"longo={item['stats_longo']['mediana']:.2f} | "
                f"delta={item['delta_temporal']:.2f}"
            )
        print()

    print("-- Insights estrategicos")
    print("-" * 50)
    maiores_pioras = sorted(
        dados_completos,
        key=lambda item: item["delta_temporal"],
        reverse=True,
    )[:5]
    maiores_melhoras = sorted(
        dados_completos,
        key=lambda item: item["delta_temporal"],
    )[:5]

    print("Principais sinais de agravamento:")
    for idx, item in enumerate(maiores_pioras, start=1):
        if item["delta_temporal"] <= 0:
            break
        print(
            f"  {idx}. {item['label_texto']} ({item['nome_dimensao']}) - delta +{item['delta_temporal']:.2f}"
        )

    print("\nPrincipais sinais de melhoria:")
    for idx, item in enumerate(maiores_melhoras, start=1):
        if item["delta_temporal"] >= 0:
            break
        print(
            f"  {idx}. {item['label_texto']} ({item['nome_dimensao']}) - delta {item['delta_temporal']:.2f}"
        )

    print("\n" + "=" * 86)


# --------------------------------------------------------------------------- #
# Execucao
# --------------------------------------------------------------------------- #

def main() -> None:
    """Funcao principal."""
    try:
        caminho = gerar_grafico_dispersao_temporal_ampliado()
        if caminho:
            print("\n>> Grafico de dispersao temporal ampliado gerado com sucesso.")
            print(f">> Arquivo de saida: {caminho}")
        else:
            print("!! Falha ao gerar o grafico ampliado.")
    except Exception as exc:  # pragma: no cover - log de erro
        print(f"!! Erro ao executar a analise ampliada: {exc}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
