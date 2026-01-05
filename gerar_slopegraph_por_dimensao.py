#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gera slopegraphs individuais para cada dimensÃ£o de risco

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

# --- CONFIG ---
INPUT_XLSX = "questionario.xlsx"
OUTPUT_DIR = "quarto/assets/slopegraphs_por_dimensao"
LABEL_WIDTH = 70

# EspaÃ§amento vertical mÃ­nimo entre variÃ¡veis (aumentado)
MIN_GAP = 0.07  # antes: 0.035


# Mapeamento das dimensÃµes baseado nos prefixos das variÃ¡veis
DIMENSOES = {
    "Economica": {
        "prefixos": ["1."],
        "cor": "#2E86AB",
        "nome": "Econ\u00f4mica"
    },
    "Ambiental": {
        "prefixos": ["2."],
        "cor": "#228B22",
        "nome": "Ambiental"
    },
    "Geopolitica": {
        "prefixos": ["3."],
        "cor": "#A23B72",
        "nome": "Geopol\u00edtica"
    },
    "Social": {
        "prefixos": ["4."],
        "cor": "#F18F01",
        "nome": "Social"
    },
    "Tecnologica": {
        "prefixos": ["5."],
        "cor": "#DC143C",
        "nome": "Tecnol\u00f3gica"
    }
}

# --- FunÃ§Ãµes utilitÃ¡rias ---

def clean_base(colname: str) -> str:
    """Remove sufixo [horizonte], prefixos numÃ©ricos '4.1- ' ou '4.1 ', normaliza espaÃ§os."""
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
def identificar_dimensao(variavel: str) -> str:
    """Identifica a dimensÃ£o de uma variÃ¡vel baseado no prefixo."""
    for dimensao, config in DIMENSOES.items():
        for prefixo in config["prefixos"]:
            if variavel.startswith(prefixo):
                return dimensao
    return "Outra"

def _spread_positions(y_vals, gap):
    """
    Espalha valores y para garantir um gap mÃ­nimo entre vizinhos.
    Faz uma passada para frente (empurra para baixo) e outra para trÃ¡s (puxa para cima).
    """
    y = np.array(y_vals, dtype=float).copy()
    # para frente
    for i in range(1, len(y)):
        if y[i] - y[i-1] < gap:
            y[i] = y[i-1] + gap
    # para trÃ¡s
    for i in range(len(y)-2, -1, -1):
        if y[i+1] - y[i] < gap:
            y[i] = y[i+1] - gap
    return y

def gerar_slopegraph_dimensao(dados_dimensao: pd.DataFrame, nome_dimensao: str, cor_dimensao: str) -> Path:
    """Gera slopegraph para uma dimensÃ£o especÃ­fica."""
    if dados_dimensao.empty:
        print(f"Sem dados para a dimensÃ£o {nome_dimensao}")
        return None

    # Filtro: apenas variÃ¡veis com mÃ©dia do Curto Prazo > 2.5
    subset = dados_dimensao[dados_dimensao["curto_mean"] > 2.5].copy()
    if subset.empty:
        print(f"Sem variÃ¡veis com mÃ©dia > 2.5 para {nome_dimensao}")
        return None

    # PosiÃ§Ã£o vertical dos rÃ³tulos
    subset["y_mid"] = (subset["curto_mean"] + subset["longo_mean"]) / 2
    subset = subset.sort_values("y_mid").reset_index(drop=True)

    # Evita colisÃµes verticais (espalhamento bidirecional com gap maior)
    subset["y_mid"] = _spread_positions(subset["y_mid"].to_numpy(), MIN_GAP)

    # Plot (tamanho dinÃ¢mico baseado no nÃºmero de variÃ¡veis) - mais alto por variÃ¡vel
    fig, ax = plt.subplots(figsize=(13, max(7, 0.50 * len(subset))))
    x_left, x_center, x_right = 0.0, 0.5, 1.0

    # Paleta com cores para variÃ¡veis individuais
    cmap = plt.get_cmap('Dark2', max(8, len(subset)))

    for i, (_, r) in enumerate(subset.iterrows()):
        color = cmap(i % cmap.N)
        y0, y1, ym = r["curto_mean"], r["longo_mean"], r["y_mid"]

        # pontos
        ax.plot([x_left],  [y0], marker='o', color=color)
        ax.plot([x_right], [y1], marker='o', color=color)

        # conector direto entre os pontos
        ax.plot([x_left, x_right], [y0, y1], linewidth=1.6, color=color)

        # valores numÃ©ricos
        ax.text(x_left - 0.02,  y0, f"{y0:.2f}", ha='right', va='center', fontsize=8, color=color)
        ax.text(x_right + 0.02, y1, f"{y1:.2f}", ha='left',  va='center', fontsize=8, color=color)

        # rÃ³tulo central com padding ligeiramente maior
        ax.text(
            x_center, ym, r["label"], ha='center', va='center', fontsize=8, color=color,
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=color, alpha=0.75, lw=0.6)
        )

    # Eixos e formataÃ§Ã£o
    ax.set_xlim(-0.3, 1.3)
    ax.set_xticks([x_left, x_right])
    ax.set_xticklabels(["Curto Prazo\n(2026\u20132027)", "Longo Prazo\n(at\u00e9 2035)"], fontsize=11, fontweight='bold')
    ax.set_ylabel("M\u00e9dia (escala de 1 a 5)", fontsize=11, fontweight='bold')
    ax.set_title(
        f"Evolu\u00e7\u00e3o Temporal dos Riscos {nome_dimensao}\n({len(subset)} vari\u00e1veis)",
        fontsize=14, fontweight='bold', pad=20, color=cor_dimensao
    )
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Ajusta o eixo y ao intervalo minimo necessario para exibir os valores
    y_min = min(subset["curto_mean"].min(), subset["longo_mean"].min(), subset["y_mid"].min())
    y_max = max(subset["curto_mean"].max(), subset["longo_mean"].max(), subset["y_mid"].max())
    faixa = max(0.2, y_max - y_min)
    pad = faixa * 0.12
    y_lim_inf = max(1.0, y_min - pad)
    y_lim_sup = min(5.0, y_max + pad)
    ax.set_ylim(y_lim_inf, y_lim_sup)

    # Linha vertical central sutil
    ax.axvline(x=x_center, color='gray', linestyle=':', alpha=0.3, linewidth=1)

    plt.tight_layout()

    # Salvar
    safe_name = nome_dimensao.lower().replace("\u00ea", "e").replace("\u00e1", "a").replace("\u00f3", "o")
    output_file = Path(OUTPUT_DIR) / f"slopegraph_{safe_name}.png"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"GrÃ¡fico salvo: {output_file}")
    return output_file

# --- Carregar e preparar dados ---

def main():
    """FunÃ§Ã£o principal."""
    parser = argparse.ArgumentParser(description="Gera slopegraphs por dimensao.")
    parser.add_argument(
        "--dimensao",
        help="Nome da dimensao (Economica, Ambiental, Geopolitica, Social, Tecnologica).",
    )
    args = parser.parse_args()

    print("=== GERANDO SLOPEGRAPHS POR DIMENSÃƒO ===")

    # Carregar dados
    xls = pd.ExcelFile(INPUT_XLSX)
    df = pd.read_excel(INPUT_XLSX, sheet_name=xls.sheet_names[0])

    # Normaliza placeholders
    df = df.replace({'-': np.nan, 'â€“': np.nan})

    # Identifica colunas de Curto e Longo
    curto_cols = [c for c in df.columns if '[Curto prazo' in c]
    longo_cols = [c for c in df.columns if '[Longo prazo' in c]

    # Mapeia colunas para nomes-base tratados
    curto_map = {c: clean_base(c) for c in curto_cols}
    longo_map = {c: clean_base(c) for c in longo_cols}

    # Apenas variÃ¡veis presentes nas duas janelas
    common_vars = sorted(set(curto_map.values()).intersection(set(longo_map.values())))

    # Calcula mÃ©dias por variÃ¡vel
    rows = []
    for var in common_vars:
        curto_col = next(k for k, v in curto_map.items() if v == var)
        longo_col = next(k for k, v in longo_map.items() if v == var)
        curto_mean = pd.to_numeric(df[curto_col], errors='coerce').mean()
        longo_mean = pd.to_numeric(df[longo_col], errors='coerce').mean()

        # Identifica a dimensÃ£o usando o nome original da coluna (com prefixo)
        dimensao = identificar_dimensao(curto_col)

        rows.append({
            "variavel": var,
            "curto_mean": curto_mean,
            "longo_mean": longo_mean,
            "dimensao": dimensao
        })

    tidy = pd.DataFrame(rows).dropna(how="all", subset=["curto_mean", "longo_mean"])
    tidy["label"] = tidy["variavel"].apply(lambda s: short_label(s, LABEL_WIDTH))

    # Debug: distribuiÃ§Ã£o das dimensÃµes
    print(f"\n=== DISTRIBUIÃ‡ÃƒO POR DIMENSÃƒO ===")
    for dimensao in tidy["dimensao"].unique():
        count = len(tidy[tidy["dimensao"] == dimensao])
        print(f"{dimensao}: {count} variÃ¡veis")

    # Gera slopegraphs por dimensÃ£o
    if args.dimensao:
        chave = args.dimensao.strip().lower()
        mapa_dimensoes = {key.lower(): key for key in DIMENSOES}
        if chave not in mapa_dimensoes:
            disponiveis = ", ".join(mapa_dimensoes.values())
            print(f"Dimensao invalida. Use uma de: {disponiveis}")
            return
        dimensoes_exec = [mapa_dimensoes[chave]]
    else:
        dimensoes_exec = list(DIMENSOES.keys())

    arquivos_gerados = []
    for dimensao in dimensoes_exec:
        config = DIMENSOES[dimensao]
        print(f"\n-- Processando dimensÃ£o: {config['nome']} (procurando: {dimensao})")
        dados_dimensao = tidy[tidy["dimensao"] == dimensao].copy()

        if not dados_dimensao.empty:
            print(f"  Encontradas {len(dados_dimensao)} variÃ¡veis")
            arquivo = gerar_slopegraph_dimensao(
                dados_dimensao,
                config["nome"],
                config["cor"]
            )
            if arquivo:
                arquivos_gerados.append(arquivo)
        else:
            print(f"  Nenhuma variÃ¡vel encontrada para {config['nome']}")

    # Resumo final
    print(f"\n=== RESUMO ===")
    print(f"Total de grÃ¡ficos gerados: {len(arquivos_gerados)}")
    for arquivo in arquivos_gerados:
        print(f"  - {arquivo.name}")

    print(f"\nTodos os grÃ¡ficos foram salvos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()


