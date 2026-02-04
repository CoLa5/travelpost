"""Para Parser (Patch).

Adds support of inline svgs in paragraphs.
"""
# ruff: noqa:E741, UP031

import importlib

from reportlab.lib.abag import ABag
import reportlab.platypus
from reportlab.platypus.paragraph import _16
from reportlab.platypus.paragraph import _56
from reportlab.platypus.paragraph import _do_dots_frag
from reportlab.platypus.paragraph import _nbspCount
from reportlab.platypus.paragraph import _trailingSpaceLength
from reportlab.platypus.paragraph import imgNormV
from reportlab.platypus.paragraph import imgVRange
from reportlab.platypus.paragraph import setXPos
from svglib.svglib import svg2rlg

_svgAttrMap = reportlab.platypus.paraparser._imgAttrMap.copy()

OrigParaParser = reportlab.platypus.paraparser.ParaParser


class ParaParser(OrigParaParser):
    # NOTE: Adds support of svg-tags

    def start_svg(self, attributes):
        A = self.getAttributes(attributes, _svgAttrMap)
        if not A.get("src"):
            self._syntax_error("<svg> needs src attribute")
        A["_selfClosingTag"] = "svg"
        self._push("svg", **A)

    def end_svg(self):
        frag = self._stack[-1]
        if not getattr(frag, "_selfClosingTag", ""):
            raise ValueError("Parser failure in <svg/>")
        defn = frag.cbDefn = ABag()
        defn.kind = "svg"
        defn.src = getattr(frag, "src", None)
        defn.drawing = svg2rlg(defn.src)
        if defn.drawing is None:
            msg = f"cannot process svg {defn.src!r:s}"
            raise ValueError(msg)
        if hasattr(frag, "width") and hasattr(frag, "height"):
            msg = f"can only set one of 'width' or 'height' of svg {defn.src!r}"
            raise ValueError(msg)
        if hasattr(frag, "width"):
            defn.drawing.renderScale = frag.width / defn.drawing.width
            defn.width = frag.width
            defn.height = defn.drawing.height * defn.drawing.renderScale
        elif hasattr(frag, "height"):
            defn.drawing.renderScale = frag.height / defn.drawing.height
            defn.height = frag.height
            defn.width = defn.drawing.width * defn.drawing.renderScale
        else:
            defn.width = defn.drawing.width
            defn.height = defn.drawing.height

        defn.valign = getattr(frag, "valign", "bottom")
        del frag._selfClosingTag
        self.handle_data("")
        self._pop("svg")


def _putFragLine(cur_x, tx, line, last, pKind):
    linkRecord = getattr(tx, "_linkRecord", lambda *args, **kwds: None)
    preformatted = tx.preformatted
    xs = tx.XtraState
    cur_y = xs.cur_y
    x0 = tx._x0
    autoLeading = xs.autoLeading
    leading = xs.leading
    cur_x += xs.leftIndent
    dal = autoLeading in ("min", "max")
    if dal:
        if autoLeading == "max":
            ascent = max(_56 * leading, line.ascent)
            descent = max(_16 * leading, -line.descent)
        else:
            ascent = line.ascent
            descent = -line.descent
        leading = ascent + descent
    if tx._leading != leading:
        tx.setLeading(leading)
    if dal:
        olb = tx._olb
        if olb is not None:
            xcy = olb - ascent
            if tx._oleading != leading:
                cur_y += leading - tx._oleading
            if abs(xcy - cur_y) > 1e-8:
                cur_y = xcy
                tx.setTextOrigin(x0, cur_y)
                xs.cur_y = cur_y
        tx._olb = cur_y - descent
        tx._oleading = leading
    ws = getattr(tx, "_wordSpace", 0)
    nSpaces = 0
    words = line.words
    AL = []
    LL = []
    us_lines = xs.us_lines
    links = xs.links
    for i, f in enumerate(words):
        if hasattr(f, "cbDefn"):
            cbDefn = f.cbDefn
            kind = cbDefn.kind
            if kind == "img":
                # draw image cbDefn,cur_y,cur_x
                txfs = tx._fontsize
                if txfs is None:
                    txfs = xs.style.fontSize
                w = imgNormV(cbDefn.width, xs.paraWidth)
                h = imgNormV(cbDefn.height, txfs)
                iy0, iy1 = imgVRange(h, cbDefn.valign, txfs)
                cur_x_s = cur_x + nSpaces * ws
                tx._canvas.drawImage(
                    cbDefn.image, cur_x_s, cur_y + iy0, w, h, mask="auto"
                )
                cur_x += w
                cur_x_s += w
                setXPos(tx, cur_x_s - tx._x0)
            # NOTE: SUPPORT of svg
            elif kind == "svg":
                # draw svg cbDefn,cur_y,cur_x
                txfs = tx._fontsize
                if txfs is None:
                    txfs = xs.style.fontSize
                if (
                    cbDefn.width == cbDefn.drawing.width
                    and cbDefn.height == cbDefn.drawing.height
                ):
                    cbDefn.drawing.renderScale = txfs / cbDefn.height
                    cbDefn.width = (
                        cbDefn.drawing.width * cbDefn.drawing.renderScale
                    )
                    cbDefn.height = txfs
                w = cbDefn.width
                h = cbDefn.height

                iy0, iy1 = imgVRange(h, cbDefn.valign, txfs)
                cur_x_s = cur_x + nSpaces * ws

                form_id = f"svg_{cbDefn.src:s}_w{w:.6f}_h{h:.6f}"
                if not tx._canvas.hasForm(form_id):
                    tx._canvas.beginForm(form_id)
                    cbDefn.drawing.drawOn(tx._canvas, 0.0, 0.0)
                    tx._canvas.endForm()
                tx._canvas.translate(cur_x_s, cur_y + iy0)
                tx._canvas.doForm(form_id)
                tx._canvas.translate(-cur_x_s, -cur_y - iy0)

                cur_x += w
                cur_x_s += w
                setXPos(tx, cur_x_s - tx._x0)
            else:
                name = cbDefn.name
                if kind == "anchor":
                    tx._canvas.bookmarkHorizontal(name, cur_x, cur_y + leading)
                else:
                    func = tx._canvas.getNamedCB(name)
                    if not func:
                        raise AttributeError(
                            "Missing %s callback attribute '%s'" % (kind, name)
                        )
                    # with open('/tmp/dbg.txt','a') as _:
                    #   print(f'{kind=} {name=} {func=}',file=_)
                    tx._canvas._curr_tx_info = dict(
                        tx=tx,
                        cur_x=cur_x,
                        cur_y=cur_y,
                        leading=leading,
                        xs=tx.XtraState,
                    )
                    try:
                        func(tx._canvas, kind, getattr(cbDefn, "label", None))
                    finally:
                        del tx._canvas._curr_tx_info
            if f is words[-1]:
                if not tx._fontname:
                    tx.setFont(xs.style.fontName, xs.style.fontSize)
                tx._textOut("", 1)
        else:
            cur_x_s = cur_x + nSpaces * ws
            end_x = cur_x_s
            fontSize = f.fontSize
            textColor = f.textColor
            rise = f.rise
            if i > 0:
                end_x = cur_x_s - (
                    0
                    if preformatted
                    else _trailingSpaceLength(words[i - 1].text, tx)
                )
            if (tx._fontname, tx._fontsize) != (f.fontName, fontSize):
                tx._setFont(f.fontName, fontSize)
            if xs.textColor != textColor:
                xs.textColor = textColor
                tx.setFillColor(textColor)
            if xs.rise != rise:
                xs.rise = rise
                tx.setRise(rise)

            # we should end stuff bfore outputting more text so we can record
            # the text code position correctly if needed
            if f.us_lines != LL:
                S = set(LL)
                NS = set(f.us_lines)
                nLL = NS - S  # new lines
                eLL = S - NS  # ending lines
                for l in eLL:
                    us_lines[l] = us_lines[l], end_x
            if f.link != AL:
                S = set(AL)
                NS = set(f.link)
                nAL = NS - S  # new linkis
                eAL = S - NS  # ending links
                for l in eAL:
                    links[l] = links[l], end_x
                    linkRecord(l, "end")
            text = f.text
            tx._textOut(text, f is words[-1])  # cheap textOut
            if f.us_lines != LL:
                for l in nLL:
                    us_lines[l] = (l, fontSize, textColor, cur_x_s), fontSize
                LL = f.us_lines
            if LL:
                for l in LL:
                    l0, fsmax = us_lines[l]
                    if fontSize > fsmax:
                        us_lines[l] = l0, fontSize

            nlo = rise - 0.2 * fontSize
            nhi = rise + fontSize
            if f.link != AL:
                for l in nAL:
                    links[l] = (l, cur_x), nlo, nhi
                    linkRecord(l, "start")
                AL = f.link
            if AL:
                for l in AL:
                    l0, lo, hi = links[l]
                    if nlo < lo or nhi > hi:
                        links[l] = l0, min(nlo, lo), max(nhi, hi)

            bg = getattr(f, "backColor", None)
            if bg and not xs.backColor:
                xs.backColor = bg
                xs.backColor_x = cur_x_s
            elif xs.backColor:
                if not bg:
                    xs.backColors.append((xs.backColor_x, end_x, xs.backColor))
                    xs.backColor = None
                elif (
                    f.backColor != xs.backColor or xs.textColor != xs.backColor
                ):
                    xs.backColors.append((xs.backColor_x, end_x, xs.backColor))
                    xs.backColor = bg
                    xs.backColor_x = cur_x_s
            txtlen = tx._canvas.stringWidth(text, tx._fontname, tx._fontsize)
            cur_x += txtlen
            nSpaces += text.count(" ") + _nbspCount(text)

    cur_x_s = cur_x + (nSpaces - 1) * ws
    if last and xs.style.endDots:
        if xs.style.wordWrap != "RTL":  # assume dots left --> right
            if pKind != "right":
                _do_dots_frag(cur_x, cur_x_s, line.maxWidth, xs, tx)
        elif pKind != "left":
            start = tx._x_offset
            _do_dots_frag(start, start, x0 - start, xs, tx, left=False)

    if LL:
        for l in LL:
            us_lines[l] = us_lines[l], cur_x_s

    if AL:
        for l in AL:
            links[l] = links[l], cur_x_s
            linkRecord(l, "end")

    if xs.backColor:
        xs.backColors.append((xs.backColor_x, cur_x_s, xs.backColor))
    if tx._x0 != x0:
        setXPos(tx, x0 - tx._x0)


reportlab.platypus.paraparser.ParaParser = ParaParser
importlib.reload(reportlab.platypus.paragraph)
reportlab.platypus.paragraph._putFragLine = _putFragLine
