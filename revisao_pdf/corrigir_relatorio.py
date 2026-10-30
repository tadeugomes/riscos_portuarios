#!/usr/bin/env python3
"""Aplica as emendas ao PDF diagramado e gera:
  - <nome> - CORRIGIDO.pdf : versão limpa, com texto e figuras corrigidos
  - <nome> - PROVA.pdf     : original com destaques e notas explicando cada emenda
  - revisao_pdf/relatorio_verificacao.txt : resultado de todas as verificações

Uso: python revisao_pdf/corrigir_relatorio.py [caminho_do_pdf]
Termina com código 1 se qualquer verificação falhar (nada é gravado como CORRIGIDO).
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pymupdf as fitz
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "revisao_pdf"))
sys.path.insert(0, str(RAIZ / "validacao"))
from motor import (apagar_faixas, corrigir_tounicode_hifen, TEXT_X, Compositor, ErroEmenda, Fontes, Linha, apagar_texto, norm)  # noqa: E402
from emendas import EMENDAS, IMAGENS, SINALIZACOES  # noqa: E402
from numeros_referencia import calcular, carregar  # noqa: E402

PADRAO = RAIZ / "RELATORIO DE RISCO GLOBAL COMPLETO-DIGITAL.pdf"
NUM_EXTENSO = {"nove": 9, "doze": 12}


# ---------------------------------------------------------------- utilidades de leitura
def linhas(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            spans = [s for s in l["spans"] if "Wingdings" not in s["font"]]
            out.append(dict(bbox=fitz.Rect(l["bbox"]), spans=spans,
                            texto="".join(s["text"] for s in spans)))
    return out


def dentro(area, r):
    return area.contains(fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))


def texto_area(page, area):
    sel = [l for l in linhas(page) if dentro(area, l["bbox"]) and l["texto"].strip()]
    sel.sort(key=lambda l: (round(l["bbox"].y0 / 3), l["bbox"].x0))
    return norm("\n".join(l["texto"] for l in sel))


def base_auto(page, area):
    sel = [l for l in linhas(page) if dentro(area, l["bbox"]) and l["texto"].strip()]
    sel.sort(key=lambda l: (l["bbox"].y0, l["bbox"].x0))
    s = next(s for s in sel[0]["spans"] if s["text"].strip())
    return s["origin"][1]


def fora_das_areas(page, areas):
    return sorted((l["texto"].strip(), tuple(round(v) for v in l["bbox"]))
                  for l in linhas(page)
                  if l["texto"].strip() and not any(dentro(a, l["bbox"]) for a in areas))


def plano(markup: str) -> str:
    return norm(markup.replace("**", "").replace("\n", " "))


# ---------------------------------------------------------------- referência numérica
def resolver(ref: dict, chave: str):
    if "|" in chave:
        pref, alts = chave.rsplit(".", 1)
        return [resolver(ref, f"{pref}.{a}")[0] for a in alts.split("|")]
    v = ref
    for parte in chave.split(".") if not chave.startswith("pct.") else ["pct", chave[4:]]:
        v = v[parte]
    return [v]


def numeros_do_rotulo(rotulo: str):
    achados = [(m.group(0), m.group(1)) for m in re.finditer(r"[+-]?(\d+(?:,\d+)?)", rotulo)]
    for palavra, n in NUM_EXTENSO.items():
        if palavra in rotulo.lower():
            achados.append((palavra, str(n)))
    return achados


def conferir_numeros(rotulo: str, valores: list) -> str | None:
    nums = numeros_do_rotulo(rotulo)
    if len(valores) == 1 and len(nums) > 1:
        # rótulos como "56 de 76": confere o primeiro número
        nums = nums[:1]
    if len(nums) != len(valores):
        return f"rótulo {rotulo!r}: {len(nums)} números para {len(valores)} valores"
    for (bruto, txt), val in zip(nums, valores):
        casas = len(txt.split(",")[1]) if "," in txt else 0
        lido = float(txt.replace(",", "."))
        if bruto.startswith("-"):
            lido = -lido
        if round(float(val), casas) != round(lido, casas) and round(abs(float(val)), casas) != round(lido, casas):
            return f"rótulo {rotulo!r}: texto diz {bruto}, base diz {val}"
    return None


# ---------------------------------------------------------------- composição de uma emenda
def compor(fontes, page, e) -> tuple[Compositor, str]:
    comp = Compositor(fontes)
    area = fitz.Rect(e["area"])
    y = base_auto(page, area)
    planos = []
    primeiro = True
    for bl in e["blocos"]:
        tipo = bl[0]
        if tipo == "b":
            markup = bl[1]
            gap = bl[2] if len(bl) > 2 else 0
            if not primeiro:
                y += gap
            comp.bullet(y)
            ult = comp.paragrafo(markup, y, TEXT_X, TEXT_X, 518.5)
            y = ult + 15
            planos.append(plano(markup))
        elif tipo == "h":
            _, txt, est, x, gap = bl
            if not primeiro:
                y += gap
            comp.checar_glifos(txt, est)
            comp.linhas.append(Linha(y, [(x, txt, est)]))
            if est == "h_pt":
                comp.faixa_da_linha(comp.linhas[-1], est)
            y += 15
            planos.append(norm(txt))
        elif tipo == "p":
            _, markup, o = bl
            if "tabela" in o:
                x, direita = o["tabela"]
                for i, txt in enumerate(markup.split("\n")):
                    comp.checar_glifos(txt, "t8")
                    if fontes.largura("UltraLight", txt, 8) > direita - x:
                        raise ErroEmenda(f"célula estoura a coluna: {txt!r}")
                    comp.linhas.append(Linha(y + 9.6 * i, [(x, txt, "t8")]))
                y += 9.6 * len(markup.split("\n"))
            else:
                if not primeiro:
                    y += o.get("gap", 0)
                lead = o.get("leading", 15)
                n0 = len(comp.linhas)
                ult = comp.paragrafo(markup, y, o["x1"], o["x2"], o.get("direita", 518.5),
                                     normal=o.get("normal", "body"), bold=o.get("bold", "lab"),
                                     leading=lead, justificar=o.get("justificar", True))
                if o.get("bold") == "h_pt":
                    comp.faixa_da_linha(comp.linhas[n0], "h_pt")
                y = ult + lead
            planos.append(plano(markup))
        elif tipo == "linha":
            _, txt, x = bl
            comp.checar_glifos(txt, "body")
            palavras = txt.split(" ")
            larg = sum(fontes.largura("UltraLight", w, 12) for w in palavras)
            gap = (518.5 - x - larg) / (len(palavras) - 1)
            xs, pecas = x, []
            for w in palavras:
                pecas.append((xs, w, "body"))
                xs += fontes.largura("UltraLight", w, 12) + gap
            comp.linhas.append(Linha(y, pecas))
            y += 15
            planos.append(norm(txt))
        elif tipo == "box38":
            planos.append(box38(fontes, comp, page, area))
        else:
            raise ErroEmenda(f"tipo de bloco desconhecido: {tipo}")
        primeiro = False
    ultima = max(l.y for l in comp.linhas)
    if ultima > e["limite"] + 0.5:
        raise ErroEmenda(f"p.{e['pag']}: composição termina em y={ultima:.1f}, limite {e['limite']}")
    return comp, " ".join(planos)


def box38(fontes, comp, page, area):
    intro = ("Foram identificados **9 riscos críticos** (pelo menos 40% em níveis altos), nas "
             "dimensões Econômica (Eco.), Geopolítica (Geo.) e Tecnológica (Tec.):")
    ult = comp.paragrafo(intro, 696.28, 136.38, 136.38, 487, normal="l10", bold="blk10",
                         leading=12, justificar=False)
    if ult > 708.3:
        raise ErroEmenda("p.38: introdução do quadro passou de 2 linhas")
    itens = [("Instabilidade política (Eco.):", "50,4%;"), ("Excesso regulatório (Eco.):", "46,4%;"),
             ("Conflitos geoeconômicos (Geo.):", "46,4%;"), ("Aumento de impostos (Eco.):", "45,6%;"),
             ("Corrupção (Eco.):", "45,6%;"), ("Infraestruturas críticas (Eco.):", "44,8%;"),
             ("Segurança computacional (Tec.):", "41,6%;"),
             ("Mão de obra em tecnologia (Tec.):", "41,6%;"),
             ("Cadeias de suprimentos (Eco.):", "40,0%.")]
    colunas = [(itens[:5], 128.0, 142.0, 303.0, 1), (itens[5:], 305.0, 318.0, 488.0, 6)]
    for lista, xn, xt, direita, n0 in colunas:
        y = 729.96
        for k, (rot, pct) in enumerate(lista):
            num = f"{n0 + k}."
            comp.checar_glifos(num, "l10b")
            comp.linhas.append(Linha(y, [(xn, num, "l10b")]))
            ult = comp.paragrafo(f"{rot} **{pct}**", y, xt, xt, direita, normal="l10", bold="l10b",
                                 leading=12, justificar=False)
            y = ult + 12
        if y - 12 > 789.97:
            raise ErroEmenda("p.38: lista em duas colunas passou de 6 linhas")
    return plano(intro) + " " + " ".join(f"{i}. {r} {p}" for i, (r, p) in enumerate(itens, 1))


# ---------------------------------------------------------------- imagens
def png_para_pdf(caminho: Path, largura_max=1700):
    im = Image.open(caminho)
    if max(im.size) > largura_max:
        im.thumbnail((largura_max, largura_max), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, format="PNG", optimize=True)
    return b.getvalue()


# ---------------------------------------------------------------- execução
def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else PADRAO
    saida_limpo = src.with_name(src.stem + " - CORRIGIDO.pdf")
    saida_prova = src.with_name(src.stem + " - PROVA.pdf")
    ref = calcular(carregar())
    log, erros = [], []

    limpo = fitz.open(src)
    fontes = Fontes(limpo)
    por_pag = {}
    for e in EMENDAS:
        por_pag.setdefault(e["pag"], []).append(fitz.Rect(e["area"]))
    antes = {p: fora_das_areas(limpo[p - 1], a) for p, a in por_pag.items()}

    esperados = []
    for i, e in enumerate(EMENDAS, 1):
        page = limpo[e["pag"] - 1]
        area = fitz.Rect(e["area"])
        txt_antes = texto_area(page, area)
        for a in e["antigo"]:
            if norm(a) not in txt_antes:
                erros.append(f"E{i:02d} p.{e['pag']}: trecho antigo esperado não encontrado: {a!r}")
        try:
            comp, novo = compor(fontes, page, e)
        except ErroEmenda as ex:
            erros.append(f"E{i:02d} p.{e['pag']}: {ex}")
            continue
        for rot, chave in e["numeros"].items():
            if norm(rot) not in novo:
                erros.append(f"E{i:02d} p.{e['pag']}: rótulo {rot!r} ausente do texto novo")
            msg = conferir_numeros(rot, resolver(ref, chave))
            if msg:
                erros.append(f"E{i:02d} p.{e['pag']}: {msg}")
        esperados.append((i, e, novo, txt_antes))
        nf = apagar_faixas(page, area)
        if nf:
            log.append(f"   E{i:02d} p.{e['pag']}: {nf} faixa(s) de título removida(s) e {len(comp.faixas)} redesenhada(s)")
        apagar_texto(page, area, manter_bullets=False)
        comp.gravar(page)

    for im in IMAGENS:
        page = limpo[im["pag"] - 1]
        page.replace_image(im["xref"], stream=png_para_pdf(RAIZ / im["arquivo"]))

    if erros:
        print("\n".join(erros))
        sys.exit(1)

    log.append(f"ToUnicode do hífen corrigido em {corrigir_tounicode_hifen(limpo)} fontes inseridas")
    tmp = saida_limpo.with_suffix(".tmp.pdf")
    limpo.save(tmp, garbage=3, deflate=True)
    limpo.close()

    # ------------------------------------------------ prova contra erro (no arquivo gravado)
    chk = fitz.open(tmp)
    for p, areas in por_pag.items():
        depois = fora_das_areas(chk[p - 1], areas)
        if depois != antes[p]:
            dif = set(antes[p]) ^ set(depois)
            erros.append(f"p.{p}: texto fora das áreas emendadas foi alterado: {sorted(dif)[:4]}")
        else:
            log.append(f"OK p.{p}: {len(depois)} linhas fora das áreas emendadas idênticas ao original")
    for i, e, novo, txt_antes in esperados:
        lido = texto_area(chk[e["pag"] - 1], fitz.Rect(e["area"]))
        duas_colunas = any(b[0] == "box38" for b in e["blocos"])
        igual = (sorted(lido.split()) == sorted(novo.split())) if duas_colunas else \
            (lido.replace(" ", "") == novo.replace(" ", ""))
        if not igual:
            erros.append(f"E{i:02d} p.{e['pag']}: texto extraído difere do composto\n  lido:  {lido}\n  novo:  {novo}")
        else:
            log.append(f"OK E{i:02d} p.{e['pag']}: texto extraído = texto composto ({len(novo)} caracteres)")
        for a in e["antigo"]:
            if norm(a) in lido and norm(a) not in novo:
                erros.append(f"E{i:02d} p.{e['pag']}: trecho antigo {a!r} ainda presente")
        for rot, chave in e["numeros"].items():
            log.append(f"   número {rot!r} = {chave} -> {resolver(ref, chave)} conferido")
    for im in IMAGENS:
        page = chk[im["pag"] - 1]
        xs = [x[0] for x in page.get_images()]
        log.append(f"OK p.{im['pag']}: imagem substituída ({len(xs)} imagem(ns) na página)")
    if len(chk) != 193:
        erros.append(f"número de páginas mudou: {len(chk)}")
    chk.close()

    if erros:
        Path(tmp).unlink()
        print("\n".join(erros))
        sys.exit(1)
    Path(tmp).replace(saida_limpo)

    # ------------------------------------------------ PDF de prova (original anotado)
    prova = fitz.open(src)
    amarelo, laranja, vermelho = (1, 0.85, 0.1), (1, 0.55, 0.1), (0.85, 0.1, 0.1)
    for i, e, novo, txt_antes in esperados:
        page = prova[e["pag"] - 1]
        area = fitz.Rect(e["area"])
        rects = [l["bbox"] for l in linhas(page) if dentro(area, l["bbox"]) and l["texto"].strip()]
        h = page.add_highlight_annot(rects)
        h.set_colors(stroke=amarelo)
        h.set_info(title="Revisão LabPortos", subject=f"Emenda {i}",
                   content=f"PROBLEMA: {e['motivo']}\n\nTEXTO CORRIGIDO:\n{novo}")
        h.update()
        n = page.add_text_annot(fitz.Point(548, area.y0 + 2), f"Emenda {i}: {e['motivo']}\n\nTEXTO CORRIGIDO:\n{novo}",
                                icon="Comment")
        n.set_colors(stroke=amarelo)
        n.set_info(title="Revisão LabPortos", subject=f"Emenda {i}")
        n.update()
    for s in SINALIZACOES:
        page = prova[s["pag"] - 1]
        area = fitz.Rect(s["area"])
        rects = [l["bbox"] for l in linhas(page) if dentro(area, l["bbox"]) and l["texto"].strip()]
        h = page.add_highlight_annot(rects)
        h.set_colors(stroke=laranja)
        h.set_info(title="Revisão LabPortos", subject="Verificar (sem emenda)", content="VERIFICAR: " + s["motivo"])
        h.update()
        n = page.add_text_annot(fitz.Point(548, area.y0 + 2), "VERIFICAR (sem emenda no PDF corrigido): " + s["motivo"],
                                icon="Help")
        n.set_colors(stroke=laranja)
        n.update()
    for im in IMAGENS:
        page = prova[im["pag"] - 1]
        r = page.get_image_rects(im["xref"])[0]
        a = page.add_rect_annot(r)
        a.set_colors(stroke=vermelho)
        a.set_border(width=1.5)
        a.set_info(title="Revisão LabPortos", subject="Figura substituída", content=im["motivo"])
        a.update()
        n = page.add_text_annot(fitz.Point(548, r.y0 + 2), "FIGURA: " + im["motivo"], icon="Comment")
        n.set_colors(stroke=vermelho)
        n.update()
    capa = prova[0]
    resumo = (f"PROVA DE REVISÃO (30/10/2026). {len(esperados)} emendas de texto (amarelo), "
              f"{len(IMAGENS)} figuras substituídas (vermelho) e {len(SINALIZACOES)} trechos a verificar "
              "sem emenda (laranja). Base de referência: questionario.xlsx, 125 respondentes, 76 variáveis; "
              "números recalculados por validacao/numeros_referencia.py.")
    n = capa.add_text_annot(fitz.Point(20, 20), resumo, icon="Note")
    n.set_info(title="Revisão LabPortos", subject="Resumo da revisão")
    n.update()
    prova.save(saida_prova, garbage=3, deflate=True)

    log.insert(0, f"Fonte: {src.name}\nCorrigido: {saida_limpo.name}\nProva: {saida_prova.name}\n"
                  f"Emendas: {len(esperados)} | Figuras: {len(IMAGENS)} | Sinalizações: {len(SINALIZACOES)}\n"
                  "Glifos: cada caractere novo foi renderizado na fonte embutida da sua sequência (sem falhas).\n"
                  "Espaço: nenhuma composição ultrapassou o limite declarado da sua área.\n")
    (RAIZ / "revisao_pdf" / "relatorio_verificacao.txt").write_text("\n".join(log), encoding="utf-8")
    print("\n".join(log[:1]))
    print("TODAS AS VERIFICAÇÕES PASSARAM")


if __name__ == "__main__":
    main()
