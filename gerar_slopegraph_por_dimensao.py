#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gera slopegraphs individuais para cada dimensão de risco

import re
from textwrap import shorten
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

# --- CONFIG ---
INPUT_XLSX = "questionario.xlsx"
OUTPUT_DIR = "quarto/assets/slopegraphs_por_dimensao"
LABEL_WIDTH = 70

# Espaçamento vertical mínimo entre variáveis (aumentado)
MIN_GAP = 0.07  # antes: 0.035

# Espaçamento horizontal para os conectores no miolo (aumentado)
GAP_X = 0.03  # antes: 0.015

# Mapeamento das dimensões baseado nos prefixos das variáveis
DIMENSOES = {
    "Economica": {
        "prefixos": ["1."],
        "cor": "#2E86AB",
        "nome": "Econômica"
    },
    "Ambiental": {
        "prefixos": ["2."],
        "cor": "#228B22",
        "nome": "Ambiental"
    },
    "Geopolitica": {
        "prefixos": ["3."],
        "cor": "#A23B72",
        "nome": "Geopolítica"
    },
    "Social": {
        "prefixos": ["4."],
        "cor": "#F18F01",
        "nome": "Social"
    },
    "Tecnologica": {
        "prefixos": ["5."],
        "cor": "#DC143C",
        "nome": "Tecnológica"
    }
}

# --- Funções utilitárias ---

def clean_base(colname: str) -> str:
    """Remove sufixo [horizonte], prefixos numéricos '4.1- ' ou '4.1 ', normaliza espaços."""
    base = re.sub(r'\s*\[.*?\]\s*', '', colname)
    base = re.sub(r'^\s*\d+(?:\.\d+)*\s*-\s*', '', base)
    base = re.sub(r'^\s*\d+(?:\.\d+)*\s*', '', base)
    return re.sub(r'\s+', ' ', base).strip()

def short_label(s: str, width=70) -> str:
    return shorten(s, width=width, placeholder="…")

def identificar_dimensao(variavel: str) -> str:
    """Identifica a dimensão de uma variável baseado no prefixo."""
    for dimensao, config in DIMENSOES.items():
        for prefixo in config["prefixos"]:
            if variavel.startswith(prefixo):
                return dimensao
    return "Outra"

def _spread_positions(y_vals, gap):
    """
    Espalha valores y para garantir um gap mínimo entre vizinhos.
    Faz uma passada para frente (empurra para baixo) e outra para trás (puxa para cima).
    """
    y = np.array(y_vals, dtype=float).copy()
    # para frente
    for i in range(1, len(y)):
        if y[i] - y[i-1] < gap:
            y[i] = y[i-1] + gap
    # para trás
    for i in range(len(y)-2, -1, -1):
        if y[i+1] - y[i] < gap:
            y[i] = y[i+1] - gap
    return y

def gerar_slopegraph_dimensao(dados_dimensao: pd.DataFrame, nome_dimensao: str, cor_dimensao: str) -> Path:
    """Gera slopegraph para uma dimensão específica."""
    if dados_dimensao.empty:
        print(f"Sem dados para a dimensão {nome_dimensao}")
        return None

    # Filtro: apenas variáveis com média do Curto Prazo > 2.5
    subset = dados_dimensao[dados_dimensao["curto_mean"] > 2.5].copy()
    if subset.empty:
        print(f"Sem variáveis com média > 2.5 para {nome_dimensao}")
        return None

    # Posição vertical dos rótulos
    subset["y_mid"] = (subset["curto_mean"] + subset["longo_mean"]) / 2
    subset = subset.sort_values("y_mid").reset_index(drop=True)

    # Evita colisões verticais (espalhamento bidirecional com gap maior)
    subset["y_mid"] = _spread_positions(subset["y_mid"].to_numpy(), MIN_GAP)

    # Plot (tamanho dinâmico baseado no número de variáveis) - mais alto por variável
    fig, ax = plt.subplots(figsize=(13, max(7, 0.50 * len(subset))))
    x_left, x_center, x_right = 0.0, 0.5, 1.0

    # Paleta com cores para variáveis individuais
    cmap = plt.get_cmap('Dark2', max(8, len(subset)))

    for i, (_, r) in enumerate(subset.iterrows()):
        color = cmap(i % cmap.N)
        y0, y1, ym = r["curto_mean"], r["longo_mean"], r["y_mid"]

        # pontos
        ax.plot([x_left],  [y0], marker='o', color=color)
        ax.plot([x_right], [y1], marker='o', color=color)

        # conectores com maior abertura no centro
        ax.plot([x_left,  x_center - GAP_X], [y0, ym], linewidth=1.6, color=color)
        ax.plot([x_right, x_center + GAP_X], [y1, ym], linewidth=1.6, color=color)

        # valores numéricos
        ax.text(x_left - 0.02,  y0, f"{y0:.2f}", ha='right', va='center', fontsize=8, color=color)
        ax.text(x_right + 0.02, y1, f"{y1:.2f}", ha='left',  va='center', fontsize=8, color=color)

        # rótulo central com padding ligeiramente maior
        ax.text(
            x_center, ym, r["label"], ha='center', va='center', fontsize=8, color=color,
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=color, alpha=0.75, lw=0.6)
        )

    # Eixos e formatação
    ax.set_xlim(-0.3, 1.3)
    ax.set_xticks([x_left, x_right])
    ax.set_xticklabels(["Curto Prazo\n(2026–2027)", "Longo Prazo\n(até 2035)"], fontsize=11, fontweight='bold')
    ax.set_ylabel("Média (escala de 1 a 5)", fontsize=11, fontweight='bold')
    ax.set_title(
        f"Evolução Temporal dos Riscos {nome_dimensao}\n({len(subset)} variáveis)",
        fontsize=14, fontweight='bold', pad=20, color=cor_dimensao
    )
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_ylim(0.8, 5.2)

    # Linha vertical central sutil
    ax.axvline(x=x_center, color='gray', linestyle=':', alpha=0.3, linewidth=1)

    plt.tight_layout()

    # Salvar
    output_file = Path(OUTPUT_DIR) / f"slopegraph_{nome_dimensao.lower().replace('ê', 'e').replace('á', 'a').replace('ó', 'o')}.png"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Gráfico salvo: {output_file}")
    return output_file

# --- Carregar e preparar dados ---

def main():
    """Função principal."""
    print("=== GERANDO SLOPEGRAPHS POR DIMENSÃO ===")

    # Carregar dados
    xls = pd.ExcelFile(INPUT_XLSX)
    df = pd.read_excel(INPUT_XLSX, sheet_name=xls.sheet_names[0])

    # Normaliza placeholders
    df = df.replace({'-': np.nan, '–': np.nan})

    # Identifica colunas de Curto e Longo
    curto_cols = [c for c in df.columns if '[Curto prazo' in c]
    longo_cols = [c for c in df.columns if '[Longo prazo' in c]

    # Mapeia colunas para nomes-base tratados
    curto_map = {c: clean_base(c) for c in curto_cols}
    longo_map = {c: clean_base(c) for c in longo_cols}

    # Apenas variáveis presentes nas duas janelas
    common_vars = sorted(set(curto_map.values()).intersection(set(longo_map.values())))

    # Calcula médias por variável
    rows = []
    for var in common_vars:
        curto_col = next(k for k, v in curto_map.items() if v == var)
        longo_col = next(k for k, v in longo_map.items() if v == var)
        curto_mean = pd.to_numeric(df[curto_col], errors='coerce').mean()
        longo_mean = pd.to_numeric(df[longo_col], errors='coerce').mean()

        # Identifica a dimensão usando o nome original da coluna (com prefixo)
        dimensao = identificar_dimensao(curto_col)

        rows.append({
            "variavel": var,
            "curto_mean": curto_mean,
            "longo_mean": longo_mean,
            "dimensao": dimensao
        })

    tidy = pd.DataFrame(rows).dropna(how="all", subset=["curto_mean", "longo_mean"])
    tidy["label"] = tidy["variavel"].apply(lambda s: short_label(s, LABEL_WIDTH))

    # Debug: distribuição das dimensões
    print(f"\n=== DISTRIBUIÇÃO POR DIMENSÃO ===")
    for dimensao in tidy["dimensao"].unique():
        count = len(tidy[tidy["dimensao"] == dimensao])
        print(f"{dimensao}: {count} variáveis")

    # Gera slopegraphs por dimensão
    arquivos_gerados = []
    for dimensao, config in DIMENSOES.items():
        print(f"\n-- Processando dimensão: {config['nome']} (procurando: {dimensao})")
        dados_dimensao = tidy[tidy["dimensao"] == dimensao].copy()

        if not dados_dimensao.empty:
            print(f"  Encontradas {len(dados_dimensao)} variáveis")
            arquivo = gerar_slopegraph_dimensao(
                dados_dimensao,
                config["nome"],
                config["cor"]
            )
            if arquivo:
                arquivos_gerados.append(arquivo)
        else:
            print(f"  Nenhuma variável encontrada para {config['nome']}")

    # Resumo final
    print(f"\n=== RESUMO ===")
    print(f"Total de gráficos gerados: {len(arquivos_gerados)}")
    for arquivo in arquivos_gerados:
        print(f"  - {arquivo.name}")

    print(f"\nTodos os gráficos foram salvos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
