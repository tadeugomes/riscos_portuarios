#!/usr/bin/env python3
"""
Gera tabelas para os apêndices contendo os maiores riscos por tipo de instalação
portuária e por região brasileira, considerando o período Imediato (2025) e
o percentual de respostas em níveis altos (notas 4 e 5).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import re

import pandas as pd

# Mapeamento das regiões brasileiras por UF
STATE_TO_REGION: Dict[str, str] = {
    "AC": "Norte",
    "AL": "Nordeste",
    "AP": "Norte",
    "AM": "Norte",
    "BA": "Nordeste",
    "CE": "Nordeste",
    "DF": "Centro-Oeste",
    "ES": "Sudeste",
    "GO": "Centro-Oeste",
    "MA": "Nordeste",
    "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "MG": "Sudeste",
    "PA": "Norte",
    "PB": "Nordeste",
    "PR": "Sul",
    "PE": "Nordeste",
    "PI": "Nordeste",
    "RJ": "Sudeste",
    "RN": "Nordeste",
    "RS": "Sul",
    "RO": "Norte",
    "RR": "Norte",
    "SC": "Sul",
    "SP": "Sudeste",
    "SE": "Nordeste",
    "TO": "Norte",
}

DIMENSION_BY_PREFIX = {
    "1": "Econômica",
    "2": "Ambiental",
    "3": "Geopolítica",
    "4": "Social",
    "5": "Tecnológica",
}

IMMEDIATE_TAG = "Imediato (2025)"
HTML_TABLE_CLASSES = ["table", "table-sm", "table-striped"]

COLUMN_LABELS_PORTOS = {
    "tipo_instalacao": "Tipo de instalação",
    "ranking": "Posição",
    "dimensao": "Dimensão",
    "risco": "Descrição do risco",
    "percentual_risco_alto": "Risco alto (4-5) %",
    "media_likert": "Média Likert",
}

COLUMN_LABELS_REGIOES = {
    "regiao": "Região",
    "ranking": "Posição",
    "dimensao": "Dimensão",
    "risco": "Descrição do risco",
    "percentual_risco_alto": "Risco alto (4-5) %",
    "media_likert": "Média Likert",
}


@dataclass(frozen=True)
class RiskColumn:
    """Representa metadados extraídos dos cabeçalhos das variáveis de risco."""

    code: str
    label: str
    period: str
    dimension: str


def extract_risk_metadata(column_name: str) -> Optional[RiskColumn]:
    """
    Extrai código, descrição resumida, período e dimensão a partir do nome da coluna.
    Espera colunas no formato '1.1 Descrição do risco. [Imediato (2025)]'.
    """
    pattern = r"^(?P<code>\d+\.\d+)\s+(?P<label>.+?)\s*\[(?P<periodo>.+?)\]\s*$"
    match = re.match(pattern, column_name.strip())
    if not match:
        return None

    code = match.group("code")
    label = match.group("label").strip()
    period = match.group("periodo").strip()
    dimension = DIMENSION_BY_PREFIX.get(code.split(".")[0], "Desconhecida")
    return RiskColumn(code=code, label=label, period=period, dimension=dimension)


def normalize_uf(value: object) -> Optional[str]:
    """Extrai a sigla da UF de strings como 'Santa Catarina (SC)'."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    if len(value) == 2 and value.isalpha():
        return value.upper()

    match = re.search(r"\(([A-Z]{2})\)", value)
    if match:
        return match.group(1)
    return None


def percentage_high_risk(series: pd.Series) -> tuple[float, int, float]:
    """
    Calcula o percentual de respostas em níveis 4-5.

    Returns:
        (percentual, total_respostas_validas, media_likert)
    """
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    total = int(numeric.count())
    if total == 0:
        return (0.0, 0, float("nan"))

    pct = float(((numeric >= 4).sum() / total) * 100.0)
    media = float(numeric.mean())
    return (pct, total, media)


def format_value(value: object) -> str:
    """Padroniza valores para exportação textual."""
    if isinstance(value, float):
        if value.is_integer():
            return f"{int(value)}"
        return f"{value:.2f}"
    return str(value)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Converte um DataFrame em tabela Markdown simples."""
    headers = [str(col) for col in df.columns]
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    rows = []
    for _, row in df.iterrows():
        values = [format_value(valor) for valor in row]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header_line, separator, *rows]) + "\n"


def dataframe_to_html(df: pd.DataFrame) -> str:
    """Converte um DataFrame em tabela HTML com classes Bootstrap."""
    return df.to_html(
        index=False,
        classes=HTML_TABLE_CLASSES,
        border=0,
        justify="left",
    )


def compute_group_table(
    df: pd.DataFrame,
    group_col: str,
    group_label: str,
    risk_columns: Dict[str, RiskColumn],
) -> pd.DataFrame:
    """Calcula métricas de risco para cada grupo informado."""

    registros: List[Dict[str, object]] = []
    for valor_grupo, subdf in df.groupby(group_col):
        if pd.isna(valor_grupo):
            continue
        valor_formatado = str(valor_grupo).strip()
        for col, meta in risk_columns.items():
            pct, total, media = percentage_high_risk(subdf[col])
            if total == 0:
                continue
            registros.append(
                {
                    group_label: valor_formatado,
                    "codigo": meta.code,
                    "dimensao": meta.dimension,
                    "risco": meta.label,
                    "periodo": meta.period,
                    "percentual_risco_alto": round(pct, 2),
                    "media_likert": round(media, 2),
                    "respostas_validas": total,
                }
            )

    if not registros:
        return pd.DataFrame()

    resultado = pd.DataFrame(registros)
    resultado["ranking"] = (
        resultado.groupby(group_label)["percentual_risco_alto"]
        .rank(method="first", ascending=False)
        .astype(int)
    )
    return resultado.sort_values([group_label, "percentual_risco_alto"], ascending=[True, False])


def export_table_formats(
    df: pd.DataFrame,
    base_path: Path,
    columns: List[str],
    rename_map: Dict[str, str],
) -> Dict[str, Path]:
    """
    Salva a tabela em CSV, Markdown e HTML e retorna caminhos gerados.
    """
    outputs: Dict[str, Path] = {}
    df_export = df[columns].rename(columns=rename_map).copy()

    csv_path = base_path.with_suffix(".csv")
    df_export.to_csv(csv_path, index=False)
    outputs["csv"] = csv_path

    markdown_path = base_path.with_suffix(".md")
    markdown_path.write_text(dataframe_to_markdown(df_export), encoding="utf-8")
    outputs["markdown"] = markdown_path

    html_path = base_path.with_suffix(".html")
    html_path.write_text(dataframe_to_html(df_export), encoding="utf-8")
    outputs["html"] = html_path

    return outputs


def criar_tabelas_apendice(
    excel_path: Path = Path("questionario.xlsx"),
    output_dir: Path = Path("quarto") / "assets" / "tabelas",
    top_n: int = 10,
) -> Dict[str, Path]:
    """
    Lê o questionário e exporta duas tabelas:
        - Top riscos por tipo de instalação portuária.
        - Top riscos por região (UF agregadas).
    """
    df = pd.read_excel(excel_path)

    col_tipo_instalacao = next(
        col for col in df.columns if "instala" in col.lower() and "portu" in col.lower()
    )
    col_uf = next(col for col in df.columns if "estado" in col.lower())

    # Seleciona apenas as colunas do período Imediato (2025)
    risk_cols: Dict[str, RiskColumn] = {}
    for col in df.columns:
        if IMMEDIATE_TAG not in col:
            continue
        meta = extract_risk_metadata(col)
        if meta:
            risk_cols[col] = meta

    if not risk_cols:
        raise RuntimeError("Nenhuma coluna de risco do período 'Imediato (2025)' foi identificada.")

    # Calcula tabelas por tipo de instalação
    tabela_portos = compute_group_table(
        df[[col_tipo_instalacao, *risk_cols.keys()]].copy(),
        group_col=col_tipo_instalacao,
        group_label="tipo_instalacao",
        risk_columns=risk_cols,
    )

    if tabela_portos.empty:
        raise RuntimeError("Não foi possível calcular a tabela por tipo de instalação.")

    tabela_portos = (
        tabela_portos.groupby("tipo_instalacao")
        .head(top_n)
        .reset_index(drop=True)
    )

    # Prepara dados de região a partir da UF
    df_regiao = df[[col_uf, *risk_cols.keys()]].copy()
    df_regiao["uf"] = df_regiao[col_uf].apply(normalize_uf)
    df_regiao["regiao"] = df_regiao["uf"].map(STATE_TO_REGION)
    df_regiao = df_regiao.dropna(subset=["regiao"])

    tabela_regioes = compute_group_table(
        df_regiao,
        group_col="regiao",
        group_label="regiao",
        risk_columns=risk_cols,
    )

    if tabela_regioes.empty:
        raise RuntimeError("Não foi possível calcular a tabela agregada por região.")

    tabela_regioes = (
        tabela_regioes.groupby("regiao")
        .head(top_n)
        .reset_index(drop=True)
    )

    # Exporta arquivos
    output_dir.mkdir(parents=True, exist_ok=True)
    colunas_exportadas = [
        "ranking",
        "dimensao",
        "risco",
        "percentual_risco_alto",
        "media_likert",
    ]

    caminhos_portos = export_table_formats(
        tabela_portos,
        output_dir / "top_riscos_por_tipo_instalacao",
        ["tipo_instalacao", *colunas_exportadas],
        COLUMN_LABELS_PORTOS,
    )
    caminhos_regioes = export_table_formats(
        tabela_regioes,
        output_dir / "top_riscos_por_regiao",
        ["regiao", *colunas_exportadas],
        COLUMN_LABELS_REGIOES,
    )

    return {
        "por_tipo_instalacao": caminhos_portos["csv"],
        "por_regiao": caminhos_regioes["csv"],
        "por_tipo_instalacao_markdown": caminhos_portos["markdown"],
        "por_regiao_markdown": caminhos_regioes["markdown"],
        "por_tipo_instalacao_html": caminhos_portos["html"],
        "por_regiao_html": caminhos_regioes["html"],
    }


if __name__ == "__main__":
    caminhos = criar_tabelas_apendice()
    print("Tabelas geradas:")
    for nome, caminho in caminhos.items():
        print(f"  - {nome}: {caminho}")
