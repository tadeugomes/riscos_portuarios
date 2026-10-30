#!/usr/bin/env python3
"""Regera as figuras da análise temporal com os 76 pares (revisão out/2026).

Saídas:
  quarto/assets/graficos_agrupados/slopegraph_centro_conectores_cor_unica.png  (Gráfico 9)
  quarto/assets/graficos_agrupados/matriz_riscos_quadrantes.png                 (Figura 1)

Os números vêm de validacao/numeros_referencia.py, a mesma base usada na
validação do texto do relatório.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "validacao"))
from numeros_referencia import carregar, calcular  # noqa: E402

SAIDA = RAIZ / "quarto" / "assets" / "graficos_agrupados"
DARK2 = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#666666"]


def br(v: float, casas: int = 2) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def encurtar(txt: str, limite: int = 68) -> str:
    txt = " ".join(txt.split())
    return txt if len(txt) <= limite else txt[: limite - 1].rstrip(" ,;") + "…"


def espalhar(ys: list[float], gap: float) -> list[float]:
    """Afasta rótulos verticalmente mantendo a ordem (de cima para baixo)."""
    ordem = sorted(range(len(ys)), key=lambda i: -ys[i])
    pos = {i: ys[i] for i in ordem}
    for _ in range(200):
        mudou = False
        for a, b in zip(ordem, ordem[1:]):
            if pos[a] - pos[b] < gap:
                d = (gap - (pos[a] - pos[b])) / 2
                pos[a] += d
                pos[b] -= d
                mudou = True
        if not mudou:
            break
    return [pos[i] for i in range(len(ys))]


def grafico_evolucao(t) -> Path:
    sel = t[t.media_curto >= 3.0].sort_values("media_curto", ascending=False).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    x0, x1, xm = 0.0, 1.0, 0.5
    mids = [(r.media_curto + r.media_longo) / 2 for r in sel.itertuples()]
    labs = espalhar(mids, 0.0235)
    yl = espalhar(list(sel.media_curto), 0.0125)
    yr = espalhar(list(sel.media_longo), 0.0125)
    for i, r in enumerate(sel.itertuples()):
        cor = DARK2[i % len(DARK2)]
        ax.plot([x0, x1], [r.media_curto, r.media_longo], color=cor, lw=1.8, zorder=2)
        ax.scatter([x0, x1], [r.media_curto, r.media_longo], color=cor, s=38, zorder=3)
        ax.text(x0 - 0.03, yl[i], br(r.media_curto), ha="right", va="center", fontsize=9, color=cor)
        ax.text(x1 + 0.03, yr[i], br(r.media_longo), ha="left", va="center", fontsize=9, color=cor)
        ax.text(xm, labs[i], encurtar(f"{r.codigo} {r.nome}"), ha="center", va="center", fontsize=8.2,
                color=cor, zorder=4,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=cor, lw=0.6, alpha=0.92))
    ymin = min(sel.media_curto.min(), sel.media_longo.min(), min(labs)) - 0.06
    ymax = max(sel.media_curto.max(), sel.media_longo.max(), max(labs)) + 0.06
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(-0.22, 1.22)
    ax.set_xticks([x0, x1], ["Curto prazo\n(2026–2027)", "Longo prazo\n(até 2035)"], fontsize=10)
    ax.set_ylabel("Média (escala de 1 a 5)", fontsize=10)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: br(v, 1)))
    ax.grid(axis="y", ls="--", alpha=0.35)
    destino = SAIDA / "slopegraph_centro_conectores_cor_unica.png"
    fig.savefig(destino, dpi=300, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return destino


def matriz(r: dict, t) -> Path:
    q = r["quadrantes"]
    alto_c, alto_l = t.med_curto >= 3, t.med_longo >= 3
    em = t[~alto_c & alto_l].dimensao.value_counts()
    cr = t[alto_c & alto_l].dimensao.value_counts()
    fig = plt.figure(figsize=(9.95, 6.36), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 995)
    ax.set_ylim(636, 0)
    ax.axis("off")
    azul = "#2b3a55"
    ax.text(555, 42, "Matriz de Riscos Globais Portuários – Análise por Quadrantes", ha="center",
            va="center", fontsize=19, fontweight="bold", color=azul)
    ax.plot([165, 945], [66, 66], color=azul, lw=1.5)

    def quadro(x, y, cor, borda, titulo, numero, sub):
        ax.add_patch(Rectangle((x - 18, y - 16), 390, 220, fill=False, ec=borda, lw=1.6))
        ax.add_patch(FancyBboxPatch((x, y), 350, 185, boxstyle="round,pad=0,rounding_size=14",
                                    fc=cor, ec="none"))
        ax.plot([x, x + 350], [y + 46, y + 46], color="white", lw=0.8, alpha=0.6)
        ax.text(x + 175, y + 25, titulo, ha="center", va="center", fontsize=18, fontweight="bold", color="white")
        ax.text(x + 175, y + 80, numero, ha="center", va="center", fontsize=21, fontweight="bold", color="white")
        for k, linha in enumerate(sub):
            ax.text(x + 175, y + 120 + 22 * k, linha, ha="center", va="center", fontsize=12.5,
                    fontweight="bold", color="white")

    def n(v):
        return "Nenhuma variável" if v == 0 else f"{v} variáveis"

    quadro(190, 125, "#f0921b", "#f0921b", "Riscos Emergentes", n(q["emergentes"]),
           [f"Ambientais ({em.get('Ambiental', 0)}), geopolíticos ({em.get('Geopolítica', 0)}),",
            f"tecnológicos ({em.get('Tecnológica', 0)}), sociais ({em.get('Social', 0)})"])
    quadro(578, 125, "#d63a2f", "#d63a2f", "Riscos Crônicos", n(q["cronicos"]),
           [f"Econômicos ({cr.get('Econômica', 0)}), tecnológicos ({cr.get('Tecnológica', 0)}),",
            f"sociais ({cr.get('Social', 0)}), ambientais ({cr.get('Ambiental', 0)}),", f"geopolíticos ({cr.get('Geopolítica', 0)})"])
    quadro(190, 352, "#4a9f3b", "#4a9f3b", "Riscos Controlados", n(q["controlados"]),
           ["Mantidos em nível baixo", "nos dois horizontes"])
    quadro(578, 352, "#8e9196", "#6b6f75", "Riscos em Melhoria", n(q["em_melhoria"]),
           ["Ausência de melhorias", "consistentes"])

    ax.add_patch(FancyArrowPatch((130, 560), (130, 100), arrowstyle="-|>,head_width=6,head_length=10",
                                 color=azul, lw=4))
    ax.add_patch(FancyArrowPatch((195, 585), (905, 585), arrowstyle="-|>,head_width=6,head_length=10",
                                 color=azul, lw=4))
    ax.text(130, 88, "Alta", ha="center", va="bottom", fontsize=15, fontweight="bold", color=azul)
    ax.text(155, 585, "Baixa", ha="center", va="center", fontsize=15, fontweight="bold", color=azul)
    ax.text(945, 585, "Alta", ha="center", va="center", fontsize=15, fontweight="bold", color=azul)
    ax.text(62, 345, "Longo prazo\n(até 2035)", ha="center", va="center", fontsize=16,
            fontweight="bold", color=azul, rotation=90)
    ax.text(555, 616, "Curto prazo (2026–2027)  ·  limiar: mediana 3,0", ha="center", va="center",
            fontsize=16, fontweight="bold", color=azul)
    destino = SAIDA / "matriz_riscos_quadrantes.png"
    fig.savefig(destino, dpi=300, facecolor="white")
    plt.close(fig)
    return destino


def main() -> None:
    t = carregar()
    r = calcular(t)
    assert r["n_pares_temporais"] == 76, r["n_pares_temporais"]
    print(grafico_evolucao(t))
    print(matriz(r, t))


if __name__ == "__main__":
    main()
