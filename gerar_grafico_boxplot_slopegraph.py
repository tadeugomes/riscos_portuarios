#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gera slopegraphs individuais por dimensão, com o MESMO visual do exemplo desejado

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
MIN_GAP = 0.035  # igual ao script de referência
FILTRO_CURTO_MIN =-np.inf  #3.0  # igual ao script de referência

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

# --- utilitárias ---

def clean_base(colname: str) -> str:
    base = re.sub(r'\s*\[.*?\]\s*', '', colname)
    base = re.sub(r'^\s*\d+(?:\.\d+)*\s*-\s*', '', base)
    base = re.sub(r'^\s*\d+(?:\.\d+)*\s*', '', base)
    return re.sub(r'\s+', ' ', base).strip()

def short_label(s: str, width=70) -> str:
    return shorten(s, width=width, placeholder="…")

def identificar_dimensao(variavel_colname: str) -> str:
    for dimensao, config in DIMENSOES.items():
        for prefixo in config["prefixos"]:
            if variavel_colname.startswith(prefixo):
                return dimensao
    return "Outra"

# --- plot de UMA dimensão com o mesmo visual do seu exemplo ---

def plot_dimensao(subset: pd.DataFrame, nome_dimensao: str, cor_dimensao: str) -> Path | None:
    if subset.empty:
        print(f"Sem dados para {nome_dimensao}")
        return None

    # rótulo central na média dos dois pontos
    subset["y_mid"] = (subset["curto_mean"] + subset["longo_mean"]) / 2
    subset = subset.sort_values("y_mid").reset_index(drop=True)

    # evita colisões (mesmo critério do script de referência)
    for i in range(1, len(subset)):
        if subset.loc[i, "y_mid"] - subset.loc[i-1, "y_mid"] < MIN_GAP:
            subset.loc[i, "y_mid"] = subset.loc[i-1, "y_mid"] + MIN_GAP

    # --- VISUAL: idêntico ao script que você aprovou ---
    fig, ax = plt.subplots(figsize=(12, max(10, 0.35 * len(subset))))
    x_left, x_center, x_right = 0.0, 0.5, 1.0

    cmap = cm.get_cmap('Dark2', max(8, len(subset)))

    for i, (_, r) in enumerate(subset.iterrows()):
        color = cmap(i % cmap.N)
        y0, y1, ym = r["curto_mean"], r["longo_mean"], r["y_mid"]

        # pontos
        ax.plot([x_left],  [y0], marker='o', color=color)
        ax.plot([x_right], [y1], marker='o', color=color)

        # conectores para o rótulo central
        ax.plot([x_left,  x_center - 0.015], [y0, ym], linewidth=1.6, color=color)
        ax.plot([x_right, x_center + 0.015], [y1, ym], linewidth=1.6, color=color)

        # valores numéricos ao lado dos pontos
        ax.text(x_left - 0.02,  y0, f"{y0:.2f}", ha='right', va='center', fontsize=8, color=color)
        ax.text(x_right + 0.02, y1, f"{y1:.2f}", ha='left',  va='center', fontsize=8, color=color)

        # rótulo central
        ax.text(x_center, ym, r["label"], ha='center', va='center', fontsize=8, color=color,
                bbox=dict(boxstyle='round,pad=0.18', fc='white', ec=color, alpha=0.7, lw=0.6))

    # Eixos/grade/limites iguais ao exemplo
    ax.set_xlim(-0.25, 1.25)
    ax.set_xticks([x_left, x_right])
    ax.set_xticklabels(["Curto Prazo\n(2026–2027)", "Longo Prazo\n(até 2035)"])
    ax.set_ylabel("Média (escala de 1 a 5)")
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # título discreto com a cor da dimensão
    ax.set_title(f"Evolução Temporal dos Riscos {nome_dimensao}", color=cor_dimensao, pad=14)

    plt.tight_layout()

    # salvar
    out = Path(OUTPUT_DIR) / f"slopegraph_{nome_dimensao.lower().replace('ê','e').replace('á','a').replace('ó','o')}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Gráfico salvo: {out}")
    return out

# --- pipeline principal ---

def main():
    print("=== GERANDO SLOPEGRAPHS POR DIMENSÃO (visual igual ao exemplo) ===")

    xls = pd.ExcelFile(INPUT_XLSX)
    df = pd.read_excel(INPUT_XLSX, sheet_name=xls.sheet_names[0])

    # normaliza placeholders
    df = df.replace({'-': np.nan, '–': np.nan})

    # identificar colunas
    curto_cols = [c for c in df.columns if '[Curto prazo' in c]
    longo_cols = [c for c in df.columns if '[Longo prazo' in c]

    # mapear para base limpa
    curto_map = {c: clean_base(c) for c in curto_cols}
    longo_map = {c: clean_base(c) for c in longo_cols}

    common_vars = sorted(set(curto_map.values()).intersection(longo_map.values()))

    # calcular médias e dimensão
    rows = []
    for var in common_vars:
        curto_col = next(k for k, v in curto_map.items() if v == var)
        longo_col = next(k for k, v in longo_map.items() if v == var)
        curto_mean = pd.to_numeric(df[curto_col], errors='coerce').mean()
        longo_mean = pd.to_numeric(df[longo_col], errors='coerce').mean()
        dimensao = identificar_dimensao(curto_col)
        rows.append({
            "variavel": var,
            "curto_mean": curto_mean,
            "longo_mean": longo_mean,
            "dimensao": dimensao
        })

    tidy = pd.DataFrame(rows).dropna(how="all", subset=["curto_mean", "longo_mean"])
    tidy["label"] = tidy["variavel"].apply(lambda s: short_label(s, LABEL_WIDTH))

    # gerar por dimensão com mesmo filtro de curto prazo > 3
    arquivos = []
    for key, cfg in DIMENSOES.items():
        dados_dim = tidy[tidy["dimensao"] == key].copy()
        dados_dim = dados_dim[dados_dim["curto_mean"] > FILTRO_CURTO_MIN]
        if dados_dim.empty:
            print(f"Nada a plotar para {cfg['nome']} (após filtro curto>{FILTRO_CURTO_MIN})")
            continue
        out = plot_dimensao(dados_dim, cfg["nome"], cfg["cor"])
        if out:
            arquivos.append(out)

    print("\n=== RESUMO ===")
    print(f"Total de gráficos: {len(arquivos)}")
    for a in arquivos:
        print(" -", a.name)
    print(f"\nArquivos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
