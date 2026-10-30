#!/usr/bin/env python3
"""Recalcula, a partir de questionario.xlsx, todos os números da análise
temporal e dos riscos imediatos citados no relatório. Saída: JSON."""
import json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DIM = {"1": "Econômica", "2": "Ambiental", "3": "Geopolítica", "4": "Social", "5": "Tecnológica"}


def horizonte(rotulo: str) -> str:
    if "Imediato" in rotulo:
        return "imediato"
    if "Curto" in rotulo:
        return "curto"
    if "Longo" in rotulo:
        return "longo"
    raise ValueError(rotulo)


def carregar():
    df = pd.read_excel(RAIZ / "questionario.xlsx")
    cols = {}
    for c in df.columns:
        m = re.match(r"\s*(\d+\.\d+)\s*(.*?)\s*\[(.*?)\]\s*$", str(c), re.S)
        if not m:
            continue
        cols.setdefault(m.group(1), {})[horizonte(m.group(3))] = c
        cols[m.group(1)].setdefault("nome", m.group(2).strip())
    def num(s):
        return pd.to_numeric(s.astype(str).str.extract(r"([1-5])")[0], errors="coerce")
    linhas = []
    for cod, v in cols.items():
        assert {"imediato", "curto", "longo"} <= v.keys(), f"variável {cod} sem os três horizontes"
        i, c, l = num(df[v["imediato"]]), num(df[v["curto"]]), num(df[v["longo"]])
        linhas.append(dict(
            codigo=cod, dimensao=DIM[cod.split(".")[0]], nome=v["nome"],
            n_imediato=int(i.notna().sum()),
            pct_alto_imediato=round(100 * (i >= 4).sum() / i.notna().sum(), 1),
            pct_alto_curto=round(100 * (c >= 4).sum() / c.notna().sum(), 1),
            pct_alto_longo=round(100 * (l >= 4).sum() / l.notna().sum(), 1),
            med_curto=float(c.median()), med_longo=float(l.median()),
            media_curto=float(c.mean()), media_longo=float(l.mean()),
        ))
    t = pd.DataFrame(linhas)
    t["delta"] = t.med_longo - t.med_curto
    t["ordem"] = t.codigo.map(lambda s: tuple(int(x) for x in s.split(".")))
    return t.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)


def calcular(t: pd.DataFrame) -> dict:
    n = len(t)
    alto_c, alto_l = t.med_curto >= 3, t.med_longo >= 3
    q = {
        "cronicos": int((alto_c & alto_l).sum()),
        "emergentes": int((~alto_c & alto_l).sum()),
        "controlados": int((~alto_c & ~alto_l).sum()),
        "em_melhoria": int((alto_c & ~alto_l).sum()),
    }
    por_dim = {}
    for d, g in t.groupby("dimensao", sort=False):
        por_dim[d] = dict(n=len(g), media_pct_alto_imediato=round(float(g.pct_alto_imediato.mean()), 1), delta_medio=round(float(g.delta.mean()), 2),
                          pioras_1=int((g.delta >= 1).sum()), melhorias_1=int((g.delta <= -1).sum()),
                          estaveis=int((g.delta == 0).sum()))
    sub = t[alto_c]
    criticos_gt40 = t[t.pct_alto_imediato > 40].sort_values("pct_alto_imediato", ascending=False)
    criticos_ge40 = t[t.pct_alto_imediato >= 40]
    top20 = t.sort_values("pct_alto_imediato", ascending=False).head(20)
    assert t.pct_alto_imediato.sort_values(ascending=False).iloc[19] > t.pct_alto_imediato.sort_values(ascending=False).iloc[20], "empate na 20a posição"
    eco20 = top20[top20.dimensao == "Econômica"]

    def ge40(col):
        g = t[t[col] >= 40]
        return {"total": len(g), **{k: int(v) for k, v in g.dimensao.value_counts().items()}}

    return {
        "top20": dict(economicos=len(eco20), media_economicos=round(float(eco20.pct_alto_imediato.mean()), 1),
                      media_geral=round(float(top20.pct_alto_imediato.mean()), 1)),
        "pct": {r.codigo: r.pct_alto_imediato for r in t.itertuples()},
        "curto_ge40": ge40("pct_alto_curto"),
        "longo_ge40": ge40("pct_alto_longo"),
        "n_pioras_1": int((t.delta >= 1).sum()),
        "grafico9_n": int((t.media_curto >= 3).sum()),
        "eco_media_curto_gt25": int(((t.dimensao == "Econômica") & (t.media_curto > 2.5)).sum()),
        "n_variaveis": n,
        "n_pares_temporais": n,
        "n_respondentes": int(t.n_imediato.max()),
        "quadrantes": q,
        "pct_cronicos": round(100 * q["cronicos"] / n, 1),
        "delta_medio_geral": round(float(t.delta.mean()), 2),
        "correlacao_medianas": round(float(np.corrcoef(t.med_curto, t.med_longo)[0, 1]), 2),
        "correlacao_medias": round(float(np.corrcoef(t.media_curto, t.media_longo)[0, 1]), 2),
        "por_dimensao": por_dim,
        "pioras_1": t[t.delta >= 1][["codigo", "dimensao", "nome"]].to_dict("records"),
        "melhorias_1": t[t.delta <= -1][["codigo", "dimensao", "nome", "med_curto", "med_longo"]].to_dict("records"),
        "estaveis": int((t.delta == 0).sum()),
        "subconjunto_mediana_curto_ge3": dict(
            n=len(sub), pct=round(100 * len(sub) / n, 1),
            delta_medio=round(float(sub.delta.mean()), 2), desvio=round(float(sub.delta.std()), 2),
            pioras=int((sub.delta > 0).sum()), melhorias=int((sub.delta < 0).sum()),
            estaveis=int((sub.delta == 0).sum()),
            pct_estaveis=round(100 * float((sub.delta == 0).mean()), 1),
            lista_pioras=sub[sub.delta > 0][["codigo", "nome", "med_curto", "med_longo"]].to_dict("records"),
            estaveis_por_dim=sub[sub.delta == 0].groupby("dimensao").size().to_dict(),
        ),
        "criticos_imediatos_gt40": criticos_gt40[["codigo", "dimensao", "nome", "pct_alto_imediato"]].to_dict("records"),
        "n_criticos_imediatos_ge40": len(criticos_ge40),
    }


if __name__ == "__main__":
    t = carregar()
    r = calcular(t)
    saida = RAIZ / "validacao" / "numeros_referencia.json"
    saida.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    t.to_csv(RAIZ / "validacao" / "pares_temporais_76.csv", index=False, encoding="utf-8")
    json.dump(r, sys.stdout, ensure_ascii=False, indent=1)
