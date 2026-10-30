"""Motor de emendas tipográficas sobre o PDF diagramado (InDesign).

Princípios
- Usa somente as fontes já embutidas no PDF (subconjuntos Andes Rounded).
- Remove apenas o texto da área emendada (fundo, fios e imagens ficam intactos).
- Cada emenda declara o texto antigo esperado na área; se não estiver lá, aborta.
- Cada caractere novo é testado por renderização na fonte da sua sequência.
- A composição precisa caber no espaço declarado; se não couber, aborta.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import pymupdf as fitz
import pyphen

_HIF = pyphen.Pyphen(lang="pt_BR")
ESPACO_MIN = 0.85  # compressão mínima do espaço na justificação, como no InDesign

FONT_XREF = {"UltraLight": 5277, "Bold": 2351, "W01Regular": 2283, "W01Bold": 2437,
             "Black": 2265, "Wingdings": 2490}

STY = {
    "body": ("UltraLight", 12, 0x000000),
    "lab": ("Bold", 12, 0x224573),
    "h_az": ("UltraLight", 12, 0x0869A6),
    "h_pt": ("W01Bold", 12, 0x000000),
    "l10": ("W01Regular", 10, 0x000000),
    "l10b": ("W01Bold", 10, 0x000000),
    "blk10": ("Black", 10, 0x000000),
    "t8": ("UltraLight", 8, 0x000000),
}

BULLET_X, TEXT_X = 139.12, 150.13


class ErroEmenda(RuntimeError):
    pass


def rgb(c: int):
    return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"-\s*\n\s*", "", s)          # junta hifenização de fim de linha
    return re.sub(r"\s+", " ", s).strip()


class Fontes:
    def __init__(self, doc: fitz.Document):
        self.buf = {k: doc.extract_font(x)[3] for k, x in FONT_XREF.items()}
        self.font = {k: fitz.Font(fontbuffer=b) for k, b in self.buf.items()}
        self._tinta: dict = {}

    def tem_tinta(self, f: str, ch: str) -> bool:
        if ch == " ":
            return True
        k = (f, ch)
        if k not in self._tinta:
            img = self._render(f, ch)
            notdef = self._render(f, "\ue000")  # ponto de código inexistente: desenha o .notdef
            self._tinta[k] = min(img) < 180 and img != notdef
        return self._tinta[k]

    def _render(self, f, ch):
        d = fitz.open()
        p = d.new_page(width=60, height=60)
        p.insert_font(fontname="F", fontbuffer=self.buf[f])
        p.insert_text((10, 45), ch, fontname="F", fontsize=36)
        return p.get_pixmap(dpi=144, colorspace=fitz.csGRAY).samples

    def largura(self, f: str, txt: str, size: float) -> float:
        return self.font[f].text_length(txt, fontsize=size)


def runs(markup: str, normal: str, bold: str):
    """'texto **negrito** texto' -> [(palavra, estilo)], palavras separadas por espaço."""
    out = []
    for i, seg in enumerate(markup.split("**")):
        st = bold if i % 2 else normal
        for w in re.split(r"(\s+)", seg):
            if w and not w.isspace():
                out.append((w, st))
            elif w:
                out.append((" ", st))
    # cola tokens sem espaço entre si (ex.: '**rótulo:**' seguido de vírgula)
    palavras, atual = [], []
    for tok, st in out:
        if tok == " ":
            if atual:
                palavras.append(atual)
                atual = []
        else:
            atual.append((tok, st))
    if atual:
        palavras.append(atual)
    return palavras  # lista de palavras; cada palavra = lista de (texto, estilo)


@dataclass
class Linha:
    y: float
    pecas: list  # [(x, texto, estilo)]


FAIXA_COR = (0.7059891819953918, 0.8079957365989685, 0.850995659828186)


@dataclass
class Compositor:
    fontes: Fontes
    linhas: list = field(default_factory=list)
    faixas: list = field(default_factory=list)   # (x0, x1, linha de base): fundo dos títulos em negrito

    def faixa_da_linha(self, linha, estilo):
        pecas = [(x, t, s) for x, t, s in linha.pecas if s == estilo]
        x0 = min(x for x, _, _ in pecas)
        x1 = max(x + self.fontes.largura(STY[s][0], t, STY[s][1]) for x, t, s in pecas)
        self.faixas.append((x0, x1, linha.y))

    def checar_glifos(self, texto: str, estilo: str):
        f = STY[estilo][0]
        falta = sorted({c for c in texto if not self.fontes.tem_tinta(f, c)})
        if falta:
            raise ErroEmenda(f"glifos ausentes na fonte {f}: {''.join(falta)!r} em {texto!r}")

    def paragrafo(self, markup: str, y: float, x1: float, x2: float, direita: float,
                  normal="body", bold="lab", leading=15.0, justificar=True) -> float:
        """Compõe um parágrafo; devolve a linha de base da última linha."""
        palavras = runs(markup, normal, bold)
        size = STY[normal][1]
        esp = self.fontes.largura(STY[normal][0], " ", size)

        def larg(p):
            return sum(self.fontes.largura(STY[s][0], t, STY[s][1]) for t, s in p)

        for p in palavras:
            for t, s in p:
                self.checar_glifos(t, s)
        linhas, atual, x0 = [], [], x1

        def cabe(lista, extra):
            usado = sum(larg(q) for q in lista) + esp * ESPACO_MIN * len(lista)
            return x0 + usado + extra <= direita + 0.01

        for p in palavras:
            w = larg(p)
            if atual and not cabe(atual, w):
                partes = self._hifenizar(p, normal, size, lambda w2: cabe(atual, w2))
                if partes:
                    atual.append([(partes[0], p[0][1])])
                    p = [(partes[1], p[0][1])]
                    w = larg(p)
                linhas.append((x0, atual))
                atual, x0 = [], x2
            if not atual and x0 + w > direita + 0.01:
                raise ErroEmenda(f"palavra maior que a coluna: {p}")
            atual.append(p)
        linhas.append((x0, atual))
        for i, (xs, ps) in enumerate(linhas):
            ultima = i == len(linhas) - 1
            total = sum(larg(p) for p in ps)
            gap = esp
            if justificar and not ultima and len(ps) > 1:
                gap = (direita - xs - total) / (len(ps) - 1)
                if gap > esp * 2.6:      # evita "rios" excessivos
                    gap = esp
            x, pecas = xs, []
            for p in ps:
                for t, s in p:
                    pecas.append((x, t, s))
                    x += self.fontes.largura(STY[s][0], t, STY[s][1])
                x += gap
            self.linhas.append(Linha(y, pecas))
            y += leading
        return y - leading

    def _hifenizar(self, palavra, normal, size, cabe):
        """Divide a palavra no ponto de hifenização mais à direita que ainda cabe na linha."""
        if len(palavra) != 1 or palavra[0][1] != normal:
            return None
        txt = palavra[0][0]
        m = re.match(r"^([A-Za-zÀ-ÿ]+)([,.;:)]*)$", txt)
        if not m or len(m.group(1)) < 6:
            return None
        f = STY[normal][0]
        for pos in sorted(_HIF.positions(m.group(1)), reverse=True):
            if pos < 2 or len(m.group(1)) - pos < 3:
                continue
            ini = txt[:pos] + "-"
            if cabe(self.fontes.largura(f, ini, size)):
                return ini, txt[pos:]
        return None

    def bullet(self, y: float):
        self.linhas.append(Linha(y, [(BULLET_X, "y", "_bullet")]))

    def gravar(self, page: fitz.Page):
        nomes = {}
        for k, b in self.fontes.buf.items():
            if k == "Wingdings":
                continue
            nomes[k] = f"Rv{k}"
            page.insert_font(fontname=nomes[k], fontbuffer=b)
        for x0, x1, y in self.faixas:
            page.draw_line(fitz.Point(x0, y - 3), fitz.Point(x1, y - 3), color=FAIXA_COR, width=12)
        for ln in self.linhas:
            for x, t, s in ln.pecas:
                if s == "_bullet":
                    # glifo 121 do subconjunto Wingdings: bbox (173,444)-(765,1036) em 2048 upm, corpo 12
                    page.draw_circle(fitz.Point(x + 2.748, ln.y - 4.336), 1.734, color=None, fill=(0, 0, 0))
                    continue
                f, size, cor = STY[s]
                page.insert_text((x, ln.y), t, fontname=nomes[f], fontsize=size, color=rgb(cor))

    def caixa(self):
        if not self.linhas:
            return None
        ys = [l.y for l in self.linhas]
        return min(ys) - 12, max(ys) + 4


def linhas_pagina(page: fitz.Page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"])
            out.append(dict(bbox=fitz.Rect(l["bbox"]), texto=txt))
    return out


def texto_na_area(page: fitz.Page, area: fitz.Rect) -> str:
    sel = [l for l in linhas_pagina(page) if area.contains(fitz.Point((l["bbox"].x0 + l["bbox"].x1) / 2,
                                                                      (l["bbox"].y0 + l["bbox"].y1) / 2))]
    sel.sort(key=lambda l: (round(l["bbox"].y0), l["bbox"].x0))
    return norm("\n".join(l["texto"] for l in sel))


def apagar_faixas(page: fitz.Page, area: fitz.Rect) -> int:
    """Remove as faixas de fundo de títulos (traço de 12 pt na cor do fundo) contidas na área."""
    n = 0
    for dr in page.get_drawings():
        r = dr["rect"]
        if dr["type"] == "s" and r.height < 1 and dr.get("width") == 12 and \
                all(abs(a - b) < 1e-3 for a, b in zip(dr.get("color") or (0, 0, 0), FAIXA_COR)) and \
                area.contains(fitz.Point(r.x0, r.y0)) and area.contains(fitz.Point(r.x1, r.y1)):
            page.add_redact_annot(fitz.Rect(r.x0 - 8, r.y0 - 10, r.x1 + 8, r.y1 + 10))
            n += 1
    if n:
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                              graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                              text=fitz.PDF_REDACT_TEXT_NONE)
    return n


def apagar_texto(page: fitz.Page, area: fitz.Rect, manter_bullets: bool):
    """Remove o texto cujas linhas têm o centro dentro da área; preserva fundo e imagens."""
    for l in page.get_text("dict")["blocks"]:
        for ln in l.get("lines", []):
            r = fitz.Rect(ln["bbox"])
            c = fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
            if not area.contains(c):
                continue
            for s in ln["spans"]:
                if manter_bullets and "Wingdings" in s["font"]:
                    continue
                if not s["text"].strip():
                    continue
                sb = fitz.Rect(s["bbox"])
                h = sb.height
                page.add_redact_annot(fitz.Rect(sb.x0 + 0.3, sb.y0 + h * 0.3, sb.x1 - 0.3, sb.y1 - h * 0.3))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                          graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                          text=fitz.PDF_REDACT_TEXT_REMOVE)


def corrigir_tounicode_hifen(doc: fitz.Document) -> int:
    """Nas fontes inseridas pela revisão (recurso /Rv*), o glifo do hífen sai mapeado para U+00AD.
    Remapeia para U+002D, para que '4-5' e 'observa-se' sejam extraídos/copiados corretamente."""
    feitos = set()
    for page in doc:
        for f in page.get_fonts(full=True):
            xref, refname = f[0], f[4]
            if not refname.startswith("Rv") or xref in feitos:
                continue
            feitos.add(xref)
            alvos = [xref]
            t, desc = doc.xref_get_key(xref, "DescendantFonts")
            tipo, tu = doc.xref_get_key(xref, "ToUnicode")
            if tipo == "xref":
                tux = int(tu.split()[0])
                cm = doc.xref_stream(tux).decode("latin-1")
                novo = cm.replace("<00AD>", "<002D>").replace("<00ad>", "<002D>")
                if novo != cm:
                    doc.update_stream(tux, novo.encode("latin-1"))
    return len(feitos)
