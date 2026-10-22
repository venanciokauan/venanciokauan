#!/usr/bin/env python3
"""Gera os SVGs do README de perfil (identidade KV//OS).

Uso:
    python tools/gerar_assets.py                  # grava em ../assets (relativo ao script)
    python tools/gerar_assets.py --out OUTRA_DIR  # grava em outra pasta
    python tools/gerar_assets.py --no-overwrite   # aborta se algum arquivo já existir

Comportamento:
  * Por padrão, SOBRESCREVE assets/banner.svg, assets/divider.svg e
    assets/signature.svg. Edições manuais nesses arquivos serão perdidas;
    altere as constantes deste script em vez disso.
  * As letras grandes (nome e marca KV//OS) são desenhadas como <path>,
    a partir de um alfabeto geométrico definido em GLYPHS. Assim o resultado
    não depende de nenhuma fonte instalada no computador de quem visualiza.
  * Só a Python 3.9+ e a biblioteca padrão são necessárias.
  * Depois de gravar, cada SVG é validado (XML bem formado, viewBox presente,
    sem scripts, sem referências externas).
"""
from __future__ import annotations

import argparse
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# --------------------------------------------------------------------------
# Paleta (altere aqui para mudar as cores de todos os assets)
# --------------------------------------------------------------------------
BG = "#08090B"      # preto quase absoluto
PANEL = "#181B20"   # cinza industrial
WHITE = "#F0F2F4"   # branco frio
GRAY = "#8B929C"    # cinza técnico
ACID = "#C7FF4A"    # verde ácido: acento, nunca preenchimento amplo
LINE = "#2A2F36"    # linhas de estrutura

# Fontes só aparecem em textos pequenos e decorativos. Toda informação
# essencial está no README.md, em texto real.
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# --------------------------------------------------------------------------
# Alfabeto geométrico. Altura fixa = 10 unidades. Cada glifo: (largura, polígonos, furos)
# --------------------------------------------------------------------------
Point = tuple[float, float]


def rect(x0: float, y0: float, x1: float, y1: float) -> list[Point]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


GLYPHS: dict[str, tuple[float, list[list[Point]], list[list[Point]]]] = {
    " ": (5.0, [], []),
    "/": (7.6, [[(5.2, 0), (7.6, 0), (2.4, 10), (0, 10)]], []),
    "K": (8.8, [
        rect(0, 0, 2.4, 10),
        [(2.4, 3.9), (6.0, 0), (8.8, 0), (4.0, 5.1), (2.4, 5.4)],
        [(2.4, 6.1), (6.0, 10), (8.8, 10), (4.0, 4.9), (2.4, 4.6)],
    ], []),
    "A": (8.8, [
        [(0, 10), (3.3, 0), (5.5, 0), (2.6, 10)],
        [(8.8, 10), (5.5, 0), (3.3, 0), (6.2, 10)],
        rect(2.2, 6.4, 6.6, 8.4),
    ], []),
    "U": (8.8, [[(0, 0), (2.4, 0), (2.4, 7.8), (6.4, 7.8), (6.4, 0), (8.8, 0),
                 (8.8, 8.2), (7.0, 10), (1.8, 10), (0, 8.2)]], []),
    "N": (8.8, [
        rect(0, 0, 2.4, 10),
        rect(6.4, 0, 8.8, 10),
        [(0, 0), (2.6, 0), (8.8, 7.4), (8.8, 10), (6.2, 10), (0, 2.6)],
    ], []),
    "V": (8.8, [
        [(0, 0), (2.7, 0), (5.7, 10), (3.1, 10)],
        [(8.8, 0), (6.1, 0), (3.1, 10), (5.7, 10)],
    ], []),
    "E": (8.2, [rect(0, 0, 2.4, 10), rect(0, 0, 8.2, 2.2),
                rect(0, 3.9, 7.0, 6.1), rect(0, 7.8, 8.2, 10)], []),
    "C": (8.8, [[(1.8, 0), (8.8, 0), (8.8, 2.2), (2.4, 2.2), (2.4, 7.8), (8.8, 7.8),
                 (8.8, 10), (1.8, 10), (0, 8.2), (0, 1.8)]], []),
    "I": (2.6, [rect(0, 0, 2.6, 10)], []),
    "O": (8.8, [[(1.8, 0), (7.0, 0), (8.8, 1.8), (8.8, 8.2), (7.0, 10), (1.8, 10),
                 (0, 8.2), (0, 1.8)]],
          [rect(2.4, 2.2, 6.4, 7.8)]),
    "S": (8.8, [
        [(1.8, 0), (8.8, 0), (8.8, 2.2), (0, 2.2), (0, 1.8)],
        rect(0, 1.8, 2.4, 5.3),
        rect(0, 3.9, 8.8, 6.1),
        rect(6.4, 4.7, 8.8, 8.2),
        [(0, 7.8), (8.8, 7.8), (8.8, 8.2), (7.0, 10), (0, 10)],
    ], []),
}
GAP = 1.6  # espaço entre letras, em unidades do glifo


def _area(pts: list[Point]) -> float:
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])) / 2


def _orient(pts: list[Point], solid: bool) -> list[Point]:
    """Sólidos sempre no mesmo sentido; furos no sentido oposto (regra nonzero)."""
    if (_area(pts) > 0) != solid:
        return pts[::-1]
    return pts


def _ring(pts: list[Point], ox: float, oy: float, sc: float) -> str:
    coords = " L".join(f"{ox + x * sc:.2f},{oy + y * sc:.2f}" for x, y in pts)
    return f"M{coords} Z"


def measure(text: str) -> float:
    """Largura em unidades de glifo."""
    return sum(GLYPHS[c][0] for c in text) + GAP * (len(text) - 1)


def text_path(text: str, x: float, y: float, scale: float) -> str:
    """Retorna o atributo 'd' de um único <path> com todas as letras."""
    missing = [c for c in text if c not in GLYPHS]
    if missing:
        raise ValueError(f"Glifos não definidos: {sorted(set(missing))}")
    parts: list[str] = []
    cx = 0.0
    for ch in text:
        width, polys, holes = GLYPHS[ch]
        for p in polys:
            parts.append(_ring(_orient(p, True), x + cx * scale, y, scale))
        for h in holes:
            parts.append(_ring(_orient(h, False), x + cx * scale, y, scale))
        cx += width + GAP
    return " ".join(parts)


def chrome_gradient(gid: str, y0: float, y1: float) -> str:
    """Gradiente cromado com linha de horizonte em 50% (coordenadas absolutas)."""
    return (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{y0:.2f}" x2="0" y2="{y1:.2f}">'
        f'<stop offset="0" stop-color="{WHITE}"/>'
        f'<stop offset="0.46" stop-color="#9AA1AA"/>'
        f'<stop offset="0.5" stop-color="#4B5058"/>'
        f'<stop offset="0.56" stop-color="#B9BFC6"/>'
        f'<stop offset="1" stop-color="#E4E7EA"/>'
        f"</linearGradient>"
    )


def svg_open(w: int, h: int, uid: str, title: str, desc: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
        f'aria-labelledby="{uid}-t {uid}-d">\n'
        f'<title id="{uid}-t">{title}</title>\n<desc id="{uid}-d">{desc}</desc>\n'
    )


# --------------------------------------------------------------------------
# Assets
# --------------------------------------------------------------------------
def banner() -> str:
    W, H = 1200, 460
    x0, y1, s2 = 72.0, 84.0, 10.5
    line1, line2 = "KAUAN", "VENANCIO"
    s1 = measure(line2) * s2 / measure(line1)  # as duas linhas ficam com a mesma largura
    h1, h2 = 10 * s1, 10 * s2
    y2 = y1 + h1 + 22

    cx, cy = 1020.0, 248.0
    a0, a1 = math.radians(-70), math.radians(-25)
    arc = (f"M{cx + 112 * math.cos(a0):.2f},{cy + 112 * math.sin(a0):.2f} "
           f"A112,112 0 0 1 {cx + 112 * math.cos(a1):.2f},{cy + 112 * math.sin(a1):.2f}")
    mono_s, os_s = 4.0, 2.2
    mono_x = cx - measure("KV") * mono_s / 2
    os_x = cx - measure("//OS") * os_s / 2

    grid = "".join(
        f'<path d="M{x},20 V440" />' for x in range(60, 1200, 60)
    ) + "".join(f'<path d="M20,{y} H1180" />' for y in range(80, 440, 60))

    out = svg_open(
        W, H, "kvbanner",
        "KAUAN VENANCIO, KV//OS",
        "Banner escuro com o nome KAUAN VENANCIO em letras geométricas cromadas, "
        "a marca KV//OS dentro de um anel técnico e a frase desenvolvedor full stack em formação.",
    )
    out += (
        "<defs>\n"
        f"{chrome_gradient('chr1', y1, y1 + h1)}\n"
        f"{chrome_gradient('chr2', y2, y2 + h2)}\n"
        f"{chrome_gradient('chr3', cy - 34, cy + 6)}\n"
        f'<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{WHITE}"/><stop offset="0.5" stop-color="{GRAY}"/>'
        f'<stop offset="1" stop-color="{WHITE}"/></linearGradient>\n'
        f'<path id="nm1" d="{text_path(line1, x0, y1, s1)}"/>\n'
        f'<path id="nm2" d="{text_path(line2, x0, y2, s2)}"/>\n'
        "</defs>\n"
        f'<rect width="{W}" height="{H}" fill="{BG}"/>\n'
        f'<g stroke="{LINE}" stroke-width="1" opacity="0.45">{grid}</g>\n'
        f'<rect x="20" y="20" width="1160" height="420" fill="none" stroke="{LINE}" stroke-width="1.5"/>\n'
        f'<path d="M20,56 H1180" stroke="{LINE}" stroke-width="1.5"/>\n'
        # barra superior (janela de um sistema operacional)
        f'<rect x="44" y="32" width="12" height="12" fill="{ACID}"/>\n'
        f'<text x="68" y="44" font-family="{MONO}" font-size="18" fill="{WHITE}">KV//OS</text>\n'
        f'<text x="152" y="44" font-family="{MONO}" font-size="18" fill="{GRAY}">~/perfil</text>\n'
        f'<g fill="none" stroke="{GRAY}" stroke-width="1.5">'
        f'<rect x="1104" y="32" width="12" height="12"/><rect x="1126" y="32" width="12" height="12"/>'
        f'<rect x="1148" y="32" width="12" height="12"/></g>\n'
        # nome: eco deslocado + preenchimento cromado
        f'<use xlink:href="#nm1" x="8" y="8" fill="none" stroke="#3A414A" stroke-width="1.5"/>\n'
        f'<use xlink:href="#nm2" x="8" y="8" fill="none" stroke="#3A414A" stroke-width="1.5"/>\n'
        f'<use xlink:href="#nm1" fill="url(#chr1)"/>\n'
        f'<use xlink:href="#nm2" fill="url(#chr2)"/>\n'
        f'<rect x="72" y="388" width="140" height="6" fill="{ACID}"/>\n'
        f'<text x="72" y="426" font-family="{MONO}" font-size="26" fill="{GRAY}">'
        f"desenvolvedor full stack em formação</text>\n"
        # painel com anel e marca
        f'<rect x="884" y="72" width="276" height="352" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>\n'
        f'<path d="M884,{cy} H1160 M{cx},72 V424" stroke="{LINE}" stroke-width="1.5"/>\n'
        f'<circle cx="{cx}" cy="{cy}" r="112" fill="none" stroke="url(#ring)" stroke-width="3"/>\n'
        f'<circle cx="{cx}" cy="{cy}" r="96" fill="none" stroke="{GRAY}" stroke-width="8" '
        f'stroke-dasharray="1.5 8.5" opacity="0.6"/>\n'
        f'<path d="{arc}" fill="none" stroke="{ACID}" stroke-width="7"/>\n'
        f'<path d="{text_path("KV", mono_x, cy - 34, mono_s)}" fill="url(#chr3)"/>\n'
        f'<path d="{text_path("//OS", os_x, cy + 24, os_s)}" fill="{ACID}"/>\n'
        # marcas de canto
        f'<g fill="none" stroke-width="3">'
        f'<path d="M20,42 V20 H42 M1158,20 H1180 V42 M20,418 V440 H42" stroke="{WHITE}"/>'
        f'<path d="M1158,440 H1180 V418" stroke="{ACID}"/></g>\n'
        "</svg>\n"
    )
    return out


def divider() -> str:
    W, H = 1200, 24
    ticks = "".join(f"M{x},9 V15 " for x in range(120, 1200, 40))
    out = svg_open(W, H, "kvdiv", "Divisor", "Linha técnica decorativa com marca //.")
    out += (
        f'<path d="M0,12 H1200" stroke="{GRAY}" stroke-width="1.5" opacity="0.55"/>\n'
        f'<path d="{ticks}" stroke="{GRAY}" stroke-width="1.5" opacity="0.4"/>\n'
        f'<rect x="0" y="2" width="72" height="20" fill="{BG}"/>\n'
        f'<path d="{text_path("//", 18, 6, 1.2)}" fill="{ACID}"/>\n'
        "</svg>\n"
    )
    return out


def signature() -> str:
    W, H = 1200, 140
    s, x, y = 5.0, 48.0, 44.0
    g1 = measure("KV") + GAP
    g2 = g1 + measure("//") + GAP
    out = svg_open(
        W, H, "kvsig", "KV//OS, Kauan Venancio",
        "Assinatura em rodapé com a marca KV//OS e o nome Kauan Venancio.",
    )
    out += (
        f"<defs>{chrome_gradient('chr', y, y + 10 * s)}</defs>\n"
        f'<rect width="{W}" height="{H}" fill="{BG}"/>\n'
        f'<rect x="0" y="0" width="160" height="4" fill="{ACID}"/>\n'
        f'<path d="M0,132 H1200" stroke="{LINE}" stroke-width="1.5"/>\n'
        f'<path d="{text_path("KV", x, y, s)}" fill="url(#chr)"/>\n'
        f'<path d="{text_path("//", x + g1 * s, y, s)}" fill="{ACID}"/>\n'
        f'<path d="{text_path("OS", x + g2 * s, y, s)}" fill="url(#chr)"/>\n'
        f'<text x="1152" y="62" text-anchor="end" font-family="{MONO}" font-size="28" fill="{WHITE}">'
        f"Kauan Venancio</text>\n"
        f'<text x="1152" y="96" text-anchor="end" font-family="{MONO}" font-size="20" fill="{GRAY}">'
        f"gerado por tools/gerar_assets.py</text>\n"
        "</svg>\n"
    )
    return out


ASSETS = {"banner.svg": banner, "divider.svg": divider, "signature.svg": signature}

# --------------------------------------------------------------------------
# Validação
# --------------------------------------------------------------------------
def validar(path: Path) -> list[str]:
    erros: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return [f"{path.name}: XML inválido ({e})"]
    if not root.tag.endswith("svg"):
        erros.append(f"{path.name}: raiz não é <svg>")
    if not root.get("viewBox"):
        erros.append(f"{path.name}: viewBox ausente")
    texto = path.read_text(encoding="utf-8").lower()
    for proibido in ("<script", "<image", "<foreignobject", "@import", "@font-face", "http://", "https://"):
        # o namespace XML usa http://www.w3.org, que é permitido
        limpo = texto.replace("http://www.w3.org", "")
        if proibido in limpo:
            erros.append(f"{path.name}: contém '{proibido}'")
    # referências internas precisam existir
    ids = {el.get("id") for el in root.iter() if el.get("id")}
    for el in root.iter():
        for k, v in el.attrib.items():
            if k.endswith("href") and v.startswith("#") and v[1:] not in ids:
                erros.append(f"{path.name}: referência quebrada {v}")
    return erros


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gera os SVGs do perfil KV//OS.")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "assets",
                    help="pasta de saída (padrão: ../assets em relação a este script)")
    ap.add_argument("--no-overwrite", action="store_true",
                    help="não sobrescreve: aborta se algum arquivo já existir")
    args = ap.parse_args(argv)

    out_dir: Path = args.out.resolve()
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Erro: não foi possível criar {out_dir}: {e}", file=sys.stderr)
        return 1

    existentes = [n for n in ASSETS if (out_dir / n).exists()]
    if args.no_overwrite and existentes:
        print(f"Abortado: já existem {', '.join(existentes)} em {out_dir}", file=sys.stderr)
        return 1

    todos_erros: list[str] = []
    for nome, fn in ASSETS.items():
        destino = out_dir / nome
        try:
            destino.write_text(fn(), encoding="utf-8")
        except (OSError, ValueError) as e:
            print(f"Erro ao gerar {nome}: {e}", file=sys.stderr)
            return 1
        todos_erros += validar(destino)
        acao = "sobrescrito" if nome in existentes else "criado"
        print(f"{acao}: {destino}")

    if todos_erros:
        print("Falhas de validação:", *todos_erros, sep="\n  - ", file=sys.stderr)
        return 2
    print("Validação OK (XML, viewBox, sem scripts/URLs externas, referências internas).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
