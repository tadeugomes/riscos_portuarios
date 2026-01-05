#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gera slopegraphs individuais por dimensÃ£o, com o MESMO visual do exemplo desejado

import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import MaxNLocator

# --- CONFIG ---
INPUT_XLSX = "questionario.xlsx"
OUTPUT_DIR = "quarto/assets/slopegraphs_por_dimensao"
LABEL_WIDTH = 70
MIN_GAP = 0.035  # igual ao script de referÃªncia
FILTRO_CURTO_MIN =-np.inf  #3.0  # igual ao script de referÃªncia

# Mapeamento das dimensÃµes baseado nos prefixos das variÃ¡veis
DIMENSOES = {
    "Economica": {
        "prefixos": ["1."],
        "cor": "#2E86AB",
        "nome": "Economica",
        "arquivo": "slopegraph_econômica.png"
    },
    "Ambiental": {
        "prefixos": ["2."],
        "cor": "#228B22",
        "nome": "Ambiental",
        "arquivo": "slopegraph_ambiental.png"
    },
    "Geopolitica": {
        "prefixos": ["3."],
        "cor": "#A23B72",
        "nome": "Geopolitica",
        "arquivo": "slopegraph_geopolítica.png"
    },
    "Social": {
        "prefixos": ["4."],
        "cor": "#F18F01",
        "nome": "Social",
        "arquivo": "slopegraph_social.png"
    },
    "Tecnologica": {
        "prefixos": ["5."],
        "cor": "#DC143C",
        "nome": "Tecnologica",
        "arquivo": "slopegraph_tecnologica.png"
    }
}

# --- utilitÃ¡rias ---

def clean_base(colname: str) -> str:
    base = re.sub(r'\s*\[.*?\]\s*', '', colname)
    base = re.sub(r'^\s*\d+(?:\.\d+)*\s*-\s*', '', base)
    base = re.sub(r'^\s*\d+(?:\.\d+)*\s*', '', base)
    return re.sub(r'\s+', ' ', base).strip()

def short_label(s: str, width=70) -> str:
    s = " ".join(s.split())
    if len(s) <= width:
        return s
    corte = s.rfind(" ", 0, width + 1)
    if corte == -1:
        return s[:width].rstrip()
    return s[:corte].rstrip()
def identificar_dimensao(variavel_colname: str) -> str:
    for dimensao, config in DIMENSOES.items():
        for prefixo in config["prefixos"]:
            if variavel_colname.startswith(prefixo):
                return dimensao
    return "Outra"

def spread_positions(y_desired, y_min, y_max, min_gap):
    y = list(y_desired)
    for i in range(1, len(y)):
        if y[i] > y[i - 1] - min_gap:
            y[i] = y[i - 1] - min_gap
    if y and y[-1] < y_min:
        shift = y_min - y[-1]
        y = [v + shift for v in y]
    for i in range(len(y) - 2, -1, -1):
        if y[i] < y[i + 1] + min_gap:
            y[i] = y[i + 1] + min_gap
    if y and y[0] > y_max:
        shift = y_max - y[0]
        y = [v + shift for v in y]
    return y


def angle_for_line(ax, x1, y1, x2, y2):
    p1 = ax.transData.transform((x1, y1))
    p2 = ax.transData.transform((x2, y2))
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    return np.degrees(np.arctan2(dy, dx))


# --- plot de UMA dimensÃ£o com o mesmo visual do seu exemplo ---

def plot_dimensao(subset: pd.DataFrame, nome_dimensao: str, cor_dimensao: str, arquivo_saida: str) -> Path | None:
    if subset.empty:
        print(f"Sem dados para {nome_dimensao}")
        return None

    subset = subset.copy()
    subset["y_mid"] = (subset["curto_mean"] + subset["longo_mean"]) / 2
    subset = subset.sort_values("y_mid", ascending=False).reset_index(drop=True)
    n = len(subset)

    fig_h = max(3.5, 0.4 * n + 1.5)
    fig, ax = plt.subplots(figsize=(12, fig_h))

    x_left, x_mid, x_right = 0.0, 0.5, 1.0
    y_min = min(subset["curto_mean"].min(), subset["longo_mean"].min())
    y_max = max(subset["curto_mean"].max(), subset["longo_mean"].max())
    rng = y_max - y_min
    pad = 0.06 * rng if rng > 0 else 0.1
    ylim_min, ylim_max = y_min - pad, y_max + pad
    ax.set_ylim(ylim_min, ylim_max)

    desired = subset["y_mid"].tolist()
    min_gap = max(0.02, (ylim_max - ylim_min) / (n * 2.2))
    y_labels = spread_positions(desired, ylim_min + pad * 0.15, ylim_max - pad * 0.15, min_gap)

    cmap = plt.get_cmap("tab20")
    color_map = {var: cmap(i % cmap.N) for i, var in enumerate(subset["variavel"].tolist())}

    for i, (_, row) in enumerate(subset.iterrows()):
        var = row["variavel"]
        label = row.get("label", var)
        c = color_map[var]
        yL, yR = row["curto_mean"], row["longo_mean"]
        yLab = y_labels[i]

        ax.plot([x_left, x_mid], [yL, yLab], linewidth=1.2, color=c)
        ax.plot([x_mid, x_right], [yLab, yR], linewidth=1.2, color=c)
        ax.scatter([x_left, x_right], [yL, yR], s=26, zorder=3, color=c)

        ax.text(x_left - 0.02, yL, f"{yL:.2f}", ha="right", va="center", fontsize=8)
        ax.text(x_right + 0.02, yR, f"{yR:.2f}", ha="left", va="center", fontsize=8)

        ang = angle_for_line(ax, x_left, yL, x_right, yR)
        ax.text(
            x_mid, yLab, label,
            ha="center", va="center",
            fontsize=9, rotation=ang, rotation_mode="anchor"
        )

    ax.set_xlim(-0.18, 1.18)
    ax.set_xticks([x_left, x_right])
    ax.set_xticklabels(["Curto prazo", "Longo prazo"], fontsize=10)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=7))
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.4)
    ax.set_ylabel("Media")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    fig.tight_layout()

    out = Path(OUTPUT_DIR) / arquivo_saida
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Grafico salvo: {out}")
    return out

# --- pipeline principal ---

def main():
    print("=== GERANDO SLOPEGRAPHS POR DIMENSÃƒO (visual igual ao exemplo) ===")

    xls = pd.ExcelFile(INPUT_XLSX)
    df = pd.read_excel(INPUT_XLSX, sheet_name=xls.sheet_names[0])

    # normaliza placeholders
    df = df.replace({'-': np.nan, 'â€“': np.nan})

    # identificar colunas
    curto_cols = [c for c in df.columns if '[Curto prazo' in c]
    longo_cols = [c for c in df.columns if '[Longo prazo' in c]

    # mapear para base limpa
    curto_map = {c: clean_base(c) for c in curto_cols}
    longo_map = {c: clean_base(c) for c in longo_cols}

    common_vars = sorted(set(curto_map.values()).intersection(longo_map.values()))

    # calcular mÃ©dias e dimensÃ£o
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

    # gerar por dimensÃ£o com mesmo filtro de curto prazo > 3
    arquivos = []
    for key, cfg in DIMENSOES.items():
        dados_dim = tidy[tidy["dimensao"] == key].copy()
        dados_dim = dados_dim[dados_dim["curto_mean"] > FILTRO_CURTO_MIN]
        if dados_dim.empty:
            print(f"Nada a plotar para {cfg['nome']} (apÃ³s filtro curto>{FILTRO_CURTO_MIN})")
            continue
        out = plot_dimensao(dados_dim, cfg["nome"], cfg["cor"], cfg["arquivo"])
        if out:
            arquivos.append(out)

    print("\n=== RESUMO ===")
    print(f"Total de grÃ¡ficos: {len(arquivos)}")
    for a in arquivos:
        print(" -", a.name)
    print(f"\nArquivos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()


