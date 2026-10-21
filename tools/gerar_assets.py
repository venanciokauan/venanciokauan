#!/usr/bin/env python3
"""Gera os SVGs do README (KV//OS). Uso: python3 tools/gerar_assets.py
Edite as constantes abaixo e rode de novo para atualizar assets/."""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)

BG, GRAY, WHITE, PURPLE, LINE = "#080808", "#A6A6A6", "#F2F2F2", "#8B5CF6", "#2A2A2A"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
CW = 0.6  # largura de caractere monoespaçado (em × font-size)

FONT = {
 "K": ["10001","10010","10100","11000","10100","10010","10001"],
 "A": ["01110","10001","10001","11111","10001","10001","10001"],
 "U": ["10001","10001","10001","10001","10001","10001","01110"],
 "N": ["10001","11001","10101","10101","10101","10011","10001"],
 "V": ["10001","10001","10001","10001","10001","01010","00100"],
 "E": ["11111","10000","10000","11110","10000","10000","11111"],
 "C": ["01111","10000","10000","10000","10000","10000","01111"],
 "I": ["11111","00100","00100","00100","00100","00100","11111"],
 "O": ["01110","10001","10001","10001","10001","10001","01110"],
}

def txt(x, y, s, size, fill, weight="normal", anchor="start", extra=""):
    """Texto com textLength fixo: largura idêntica em qualquer sistema."""
    w = round(len(s) * size * CW, 1)
    if anchor == "end":
        x = x - w
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" textLength="{w}" '
            f'lengthAdjust="spacingAndGlyphs" {extra}>{s}</text>')

def pixel_name(text, cell, x0, y0):
    rects, cx = [], 0
    for ch in text:
        if ch == " ":
            cx += 3
            continue
        for r, row in enumerate(FONT[ch]):
            for c, bit in enumerate(row):
                if bit == "1":
                    rects.append(f'<rect x="{x0 + (cx + c) * cell}" y="{y0 + r * cell}" '
                                 f'width="{cell - 2}" height="{cell - 2}" rx="1"/>')
        cx += 6
    return "\n".join(rects)

def corner(x, y, dx, dy, n=26):
    return (f'<path d="M{x} {y + dy * n} V{y} H{x + dx * n}" fill="none" '
            f'stroke="{PURPLE}" stroke-width="2.5"/>')

# ───────────────────────── BANNER ─────────────────────────
def banner():
    W, H, cell = 1200, 420, 13
    name_w = 80 * cell
    x0, y0 = (W - name_w) // 2, 118
    name = pixel_name("KAUAN VENANCIO", cell, x0, y0)
    sub = "TÉCNICO EM INFORMÁTICA PARA INTERNET / ENGENHARIA DE SOFTWARE"
    prompt = "kv@os:~$"
    cmd = "construir --entender --refazer"
    p_size = 22
    cur_x = 80 + (len(prompt) + 1 + len(cmd)) * p_size * CW + 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="KAUAN VENANCIO — banner do perfil, sistema KV//OS">
<title>KAUAN VENANCIO</title>
<defs>
 <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".035"/></pattern>
 <linearGradient id="chrome" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y0 + 7 * cell}">
  <stop offset="0" stop-color="#FFFFFF"/><stop offset=".46" stop-color="#B6B6C4"/>
  <stop offset=".5" stop-color="#55556A"/><stop offset=".54" stop-color="#CFCFDC"/><stop offset="1" stop-color="#F2F2F2"/>
 </linearGradient>
 <clipPath id="slice"><rect x="0" y="{y0 + 30}" width="{W}" height="13"/></clipPath>
 <g id="nm">{name}</g>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" fill="none" stroke="{LINE}"/>
{corner(14, 14, 1, 1)}{corner(W - 14, 14, -1, 1)}{corner(14, H - 14, 1, -1)}{corner(W - 14, H - 14, -1, -1)}

{txt(48, 50, "KV//OS · SHELL EXPERIMENTAL v0.1", 20, GRAY)}
{txt(W - 48, 50, "SESSÃO 0x4B56 · ATIVA", 20, GRAY, anchor="end")}
<circle cx="{W - 48 - 21 * 20 * CW - 16}" cy="44" r="5" fill="{PURPLE}"><animate attributeName="opacity" values="1;.15;1" dur="2.4s" repeatCount="indefinite"/></circle>
<path d="M48 68H{W - 48}" stroke="{LINE}"/>

<use xlink:href="#nm" href="#nm" x="4" y="4" fill="{PURPLE}" opacity=".5"/>
<use xlink:href="#nm" href="#nm" fill="url(#chrome)"/>
<g clip-path="url(#slice)"><use xlink:href="#nm" href="#nm" fill="{PURPLE}">
 <animateTransform attributeName="transform" type="translate" values="0 0;0 0;16 0;-10 0;0 0;0 0" keyTimes="0;.86;.88;.91;.93;1" dur="7s" repeatCount="indefinite"/>
</use></g>

{txt(x0, 262, sub, 21, GRAY)}
{txt(80, 322, prompt, p_size, PURPLE, "bold")}
{txt(80 + (len(prompt) + 1) * p_size * CW, 322, cmd, p_size, WHITE)}
<rect x="{cur_x}" y="304" width="13" height="22" fill="{PURPLE}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" repeatCount="indefinite"/></rect>

<path d="M48 366H{W - 48}" stroke="{LINE}"/>
{txt(48, 396, "N 00°00′00″  W 000°00′00″  [coord. decorativa]", 18, "#6E6E6E")}
{txt(W - 48, 396, "FRONT · BACK · DADOS", 18, "#6E6E6E", anchor="end")}
<rect x="0" y="-4" width="{W}" height="3" fill="#fff" opacity=".06"><animate attributeName="y" values="-4;{H}" dur="5.5s" repeatCount="indefinite"/></rect>
</svg>'''

# ───────────────────────── CABEÇALHOS DE SEÇÃO ─────────────────────────
def header(idx, title, meta):
    W, H = 1200, 64
    s_idx, s_ttl = 30, 30
    xi = 24
    xt = xi + (len(idx) + 1) * s_idx * CW
    xe = xt + len(title) * s_ttl * CW + 24
    xm = W - 24 - len(meta) * 18 * CW
    ticks = "".join(f'<path d="M{x} 28v8" stroke="{LINE}"/>' for x in range(int(xe), int(xm - 20), 24))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{idx} {title}">
<title>{idx} {title}</title>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="{LINE}"/>
{txt(xi, 42, idx, s_idx, PURPLE, "bold")}
{txt(xt, 42, title, s_ttl, WHITE, "bold")}
<path d="M{xe} 32H{xm - 20}" stroke="{LINE}"/>{ticks}
{txt(W - 24, 39, meta, 18, "#6E6E6E", anchor="end")}
<rect x="{xe}" y="29" width="6" height="6" fill="{PURPLE}"><animate attributeName="x" values="{xe};{xm - 26};{xe}" dur="9s" repeatCount="indefinite"/></rect>
</svg>'''

# ───────────────────────── MÓDULOS (STACK) ─────────────────────────
def modules():
    W, rowh, gap = 1200, 118, 16
    rows = [
        ("[01]", "INTERFACE", "camada visível", ["HTML5", "CSS3", "JavaScript", "React"]),
        ("[02]", "LÓGICA E SERVIDOR", "camada de regras", ["Python", "Java", "PHP"]),
        ("[03]", "DATA SYSTEMS", "camada de dados", ["MySQL", "MariaDB"]),
    ]
    H = len(rows) * rowh + (len(rows) - 1) * gap
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" '
           f'aria-label="Módulos: Interface (HTML5, CSS3, JavaScript, React); Lógica e Servidor (Python, Java, PHP); Data Systems (MySQL, MariaDB)">',
           '<title>Módulos da stack</title>', f'<rect width="{W}" height="{H}" fill="{BG}"/>']
    for i, (idx, name, sub, techs) in enumerate(rows):
        y = i * (rowh + gap)
        out.append(f'<rect x="0.5" y="{y + .5}" width="{W - 1}" height="{rowh - 1}" fill="#0D0D0D" stroke="{LINE}"/>')
        out.append(f'<rect x="0" y="{y}" width="5" height="{rowh}" fill="{PURPLE}"/>')
        out.append(txt(28, y + 52, idx, 28, PURPLE, "bold"))
        out.append(txt(28 + 5 * 28 * CW, y + 52, name, 28, WHITE, "bold"))
        out.append(txt(28, y + 90, sub, 18, "#6E6E6E"))
        x = 470
        for t in techs:
            fs = 26
            w = round(len(t) * fs * CW + 32, 1)
            out.append(f'<rect x="{x}" y="{y + 31}" width="{w}" height="56" fill="none" stroke="{GRAY}" stroke-opacity=".55"/>')
            out.append(f'<path d="M{x} {y + 31}h8M{x} {y + 31}v8" stroke="{PURPLE}" stroke-width="2.5"/>')
            out.append(txt(x + 16, y + 67, t, fs, WHITE))
            x += w + 16
    out.append("</svg>")
    return "\n".join(out)

def save(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)

save("banner.svg", banner())
save("h-identidade.svg", header("[01]", "IDENTIDADE", "SYS/ID"))
save("h-modulos.svg", header("[02]", "MÓDULOS", "SYS/STACK"))
save("h-archive.svg", header("[03]", "PROJECT_ARCHIVE", "SYS/ARQ"))
save("h-manifesto.svg", header("[04]", "MANIFESTO", "SYS/TXT"))
save("h-sinal.svg", header("[05]", "SINAL", "SYS/COM"))
save("modules.svg", modules())
print("ok")
