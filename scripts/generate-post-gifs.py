"""
Generate branded GIF cards for winmdPDF social posts.
Each GIF tells a visual story specific to its angle.

ELI5       — animated editor: markdown typed → preview renders → PDF exported
Technical  — architecture flow diagram building step by step
Why built  — before/after: web+Docker complexity → just open the app
Unique     — Mermaid code → diagram renders → "in PDF too"
Story      — re-entering settings repeatedly → winmdPDF remembers them

LinkedIn: 1200x628   Twitter: 1200x675
Colors from renderer/app/globals.css
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = (15,  23,  42)
TEXT    = (226, 232, 240)
ACCENT  = (129, 140, 248)
MUTED   = (100, 116, 139)
BORDER  = (51,  65,  85)
SURFACE = (30,  41,  59)
GREEN   = (52,  211, 153)
RED     = (248, 113, 113)

FONT_DIR = "C:/Windows/Fonts/"
OUT_DIR  = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "posts", "gifs"))

# ── Font loader ───────────────────────────────────────────────────────────────
def _font(names, size):
    for n in names + ["verdana.ttf"]:
        try: return ImageFont.truetype(os.path.join(FONT_DIR, n), size)
        except OSError: pass
    return ImageFont.load_default()

def reg(size):  return _font(["segoeui.ttf",  "arial.ttf"],   size)
def bold(size): return _font(["segoeuib.ttf", "arialbd.ttf"], size)
def mono(size): return _font(["consola.ttf",  "cour.ttf", "lucon.ttf"], size)

# Pre-load
FB   = bold(38)   # brand
FL   = reg(22)    # label / badge
FS   = reg(18)    # small
FBD  = bold(28)   # body bold
FBR  = reg(26)    # body regular
FH   = bold(32)   # heading in preview
FM   = mono(20)   # monospace code
FURL = reg(20)    # footer url
FBT  = bold(20)   # button text

# ── Helpers ───────────────────────────────────────────────────────────────────
def new_frame(W, H):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    return img, draw

def header(draw, W, subtitle=""):
    draw.rectangle([0, 0, 7, 999], fill=ACCENT)
    draw.text((44, 34), "winmdPDF", font=FB, fill=ACCENT)
    if subtitle:
        sw = draw.textbbox((0, 0), subtitle, font=FL)[2]
        draw.text((W - sw - 44, 42), subtitle, font=FL, fill=MUTED)
    draw.rectangle([44, 86, W - 44, 88], fill=BORDER)

def footer(draw, W, H, label):
    draw.rectangle([44, H - 60, W - 44, H - 58], fill=BORDER)
    draw.text((44, H - 46), label, font=FURL, fill=MUTED)
    uw = draw.textbbox((0, 0), "mdpdf.whhite.com", font=FURL)[2]
    draw.text((W - uw - 44, H - 46), "mdpdf.whhite.com", font=FURL, fill=MUTED)

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textbbox((0, 0), test, font=font)[2] > max_w and cur:
            lines.append(" ".join(cur)); cur = [w]
        else: cur.append(w)
    if cur: lines.append(" ".join(cur))
    return lines

def arrow_right(draw, x1, y, x2, color=ACCENT, width=3):
    draw.line([(x1, y), (x2 - 10, y)], fill=color, width=width)
    draw.polygon([(x2, y), (x2-12, y-6), (x2-12, y+6)], fill=color)

def arrow_down(draw, x, y1, y2, color=ACCENT, width=3):
    draw.line([(x, y1), (x, y2 - 10)], fill=color, width=width)
    draw.polygon([(x, y2), (x-6, y2-12), (x+6, y2-12)], fill=color)

def box(draw, x1, y1, x2, y2, label, sublabel="", outline=BORDER, fill=SURFACE, lcolor=TEXT):
    draw.rounded_rectangle([x1, y1, x2, y2], radius=8, fill=fill, outline=outline)
    lw = draw.textbbox((0, 0), label, font=FBR)[2]
    cx = x1 + (x2 - x1 - lw) // 2
    cy = y1 + (y2 - y1) // 2 - (18 if sublabel else 9)
    draw.text((cx, cy), label, font=FBR, fill=lcolor)
    if sublabel:
        sw = draw.textbbox((0, 0), sublabel, font=FS)[2]
        cx2 = x1 + (x2 - x1 - sw) // 2
        draw.text((cx2, cy + 28), sublabel, font=FS, fill=MUTED)

def badge(draw, cx, cy, text, bg=SURFACE, fg=ACCENT):
    tw = draw.textbbox((0, 0), text, font=FL)[2]
    x1, x2 = cx - tw//2 - 14, cx + tw//2 + 14
    draw.rounded_rectangle([x1, cy - 16, x2, cy + 16], radius=8, fill=bg, outline=fg)
    draw.text((x1 + 14, cy - 12), text, font=FL, fill=fg)

def save_gif(frames_ms, filename):
    imgs      = [f for f, _ in frames_ms]
    durations = [ms for _, ms in frames_ms]
    path      = os.path.join(OUT_DIR, filename)
    for colors in (128, 64):
        q = [i.quantize(colors=colors, dither=0) for i in imgs]
        q[0].save(path, save_all=True, append_images=q[1:],
                  duration=durations, loop=0, optimize=True)
        kb = os.path.getsize(path) / 1000
        if kb <= 500: break
    print(f"  {filename:<44}  {kb:.0f} KB")

# ─────────────────────────────────────────────────────────────────────────────
# ELI5 — animate the purpose: Markdown typed → preview renders → PDF exported
# ─────────────────────────────────────────────────────────────────────────────
def eli5_frames(W, H):
    PAD   = 50
    TOP   = 104
    BOT   = H - 68
    PH    = BOT - TOP
    PW    = (W - PAD * 3) // 2
    LX    = PAD
    RX    = PAD * 2 + PW
    frames = []

    MD_LINES = [
        ("# My Document",      ACCENT),
        ("",                   TEXT),
        ("Write in **bold**,", TEXT),
        ("add bullet lists,",  TEXT),
        ("even diagrams.",     TEXT),
    ]

    def base(subtitle=""):
        img, draw = new_frame(W, H)
        header(draw, W, subtitle)
        footer(draw, W, H, "ELI5")
        return img, draw

    # Frame 1 — empty split pane
    img, draw = base()
    draw.rounded_rectangle([LX, TOP, LX+PW, TOP+PH], radius=8, fill=SURFACE, outline=BORDER)
    draw.text((LX+18, TOP+14), "Markdown", font=FL, fill=MUTED)
    draw.rounded_rectangle([RX, TOP, RX+PW, TOP+PH], radius=8, fill=SURFACE, outline=BORDER)
    draw.text((RX+18, TOP+14), "Preview", font=FL, fill=MUTED)
    frames.append((img, 700))

    # Frame 2 — markdown text appears on left
    img, draw = base()
    draw.rounded_rectangle([LX, TOP, LX+PW, TOP+PH], radius=8, fill=SURFACE, outline=ACCENT)
    draw.text((LX+18, TOP+14), "Markdown", font=FL, fill=ACCENT)
    ty = TOP + 52
    for line, color in MD_LINES:
        if line: draw.text((LX+18, ty), line, font=FM, fill=color)
        ty += 34
    draw.rounded_rectangle([RX, TOP, RX+PW, TOP+PH], radius=8, fill=SURFACE, outline=BORDER)
    draw.text((RX+18, TOP+14), "Preview", font=FL, fill=MUTED)
    frames.append((img, 1000))

    # Frame 3 — right panel renders
    img, draw = base()
    draw.rounded_rectangle([LX, TOP, LX+PW, TOP+PH], radius=8, fill=SURFACE, outline=BORDER)
    draw.text((LX+18, TOP+14), "Markdown", font=FL, fill=MUTED)
    ty = TOP + 52
    for line, _ in MD_LINES:
        if line: draw.text((LX+18, ty), line, font=FM, fill=MUTED)
        ty += 34
    draw.rounded_rectangle([RX, TOP, RX+PW, TOP+PH], radius=8, fill=(20, 32, 54), outline=ACCENT)
    draw.text((RX+18, TOP+14), "Preview", font=FL, fill=ACCENT)
    draw.text((RX+18, TOP+50), "My Document", font=FH, fill=TEXT)
    draw.rectangle([RX+18, TOP+88, RX+PW-18, TOP+90], fill=BORDER)
    draw.text((RX+18, TOP+100), "Write in bold, add bullet", font=FBR, fill=TEXT)
    draw.text((RX+18, TOP+132), "lists, even diagrams.", font=FBR, fill=TEXT)
    draw.text((RX+26, TOP+172), "•  Item one", font=FBR, fill=MUTED)
    draw.text((RX+26, TOP+204), "•  Item two", font=FBR, fill=MUTED)
    frames.append((img, 1000))

    # Frame 4 — Export button lit up
    img, draw = base()
    draw.rounded_rectangle([LX, TOP, LX+PW, TOP+PH], radius=8, fill=SURFACE, outline=BORDER)
    draw.rounded_rectangle([RX, TOP, RX+PW, TOP+PH], radius=8, fill=(20, 32, 54), outline=BORDER)
    bw, bh = 220, 52
    bx = W//2 - bw//2
    by = TOP + PH//2 - bh//2
    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=10, fill=ACCENT)
    tw = draw.textbbox((0,0), "Export PDF", font=FBT)[2]
    draw.text((bx + (bw-tw)//2, by+14), "Export PDF", font=FBT, fill=BG)
    frames.append((img, 700))

    # Frame 5 — PDF icon + filename
    img, draw = base()
    draw.rounded_rectangle([LX, TOP, LX+PW, TOP+PH], radius=8, fill=SURFACE, outline=BORDER)
    draw.rounded_rectangle([RX, TOP, RX+PW, TOP+PH], radius=8, fill=(20, 32, 54), outline=BORDER)
    ix = W//2 - 70; iy = TOP + PH//2 - 70
    draw.rounded_rectangle([ix, iy, ix+140, iy+110], radius=12, fill=SURFACE, outline=ACCENT)
    pw = draw.textbbox((0,0), "PDF", font=bold(42))[2]
    draw.text((ix + (140-pw)//2, iy+26), "PDF", font=bold(42), fill=ACCENT)
    fn = "my-document.pdf"
    fw = draw.textbbox((0,0), fn, font=FS)[2]
    draw.text((W//2 - fw//2, iy+126), fn, font=FS, fill=MUTED)
    frames.append((img, 2200))

    return frames

# ─────────────────────────────────────────────────────────────────────────────
# Technical — architecture flow builds step by step
# ─────────────────────────────────────────────────────────────────────────────
def technical_frames(W, H):
    frames = []
    # 5 boxes horizontal: Renderer → IPC → Main → printToPDF → PDF
    # Layout: centered row, boxes + arrows
    BW, BHT = 168, 70     # box width, height
    GAP     = 44           # arrow gap between boxes
    STEP    = BW + GAP
    N       = 5
    ROW_W   = N * BW + (N-1) * GAP
    X0      = (W - ROW_W) // 2
    BY      = H // 2 - BHT // 2 - 10

    BOXES = [
        ("Renderer",      "Next.js static"),
        ("IPC",           "contextBridge"),
        ("Electron Main", "main process"),
        ("printToPDF()",  "webContents"),
        ("PDF",           "output"),
    ]
    OUTLINES = [BORDER, BORDER, BORDER, BORDER, ACCENT]
    LCOLORS  = [TEXT,   TEXT,   TEXT,   TEXT,   ACCENT]

    def base():
        img, draw = new_frame(W, H)
        header(draw, W, "Technical")
        footer(draw, W, H, "Technical")
        return img, draw

    for n_visible in range(1, 6):
        img, draw = base()
        for i in range(n_visible):
            bx = X0 + i * STEP
            is_last = (i == n_visible - 1)
            outline = ACCENT if is_last else OUTLINES[i]
            lc      = ACCENT if is_last else LCOLORS[i]
            box(draw, bx, BY, bx+BW, BY+BHT,
                BOXES[i][0], BOXES[i][1], outline=outline, lcolor=lc)
            if i < n_visible - 1:
                arrow_right(draw, bx+BW, BY+BHT//2, bx+BW+GAP)

        # On last frame add "One Chromium" badge above and hold longer
        if n_visible == 5:
            badge(draw, W//2, BY - 46, "Single Chromium  -  no Puppeteer", bg=SURFACE, fg=GREEN)

        hold = 2200 if n_visible == 5 else 700
        frames.append((img, hold))

    return frames

# ─────────────────────────────────────────────────────────────────────────────
# Why built — web+Docker → winmdPDF, no Docker
# ─────────────────────────────────────────────────────────────────────────────
def why_frames(W, H):
    frames = []
    CX = W // 2
    MID_Y = H // 2 + 10

    def base():
        img, draw = new_frame(W, H)
        header(draw, W, "Why we built it")
        footer(draw, W, H, "Why we built it")
        return img, draw

    # Frame 1 — web version box
    img, draw = base()
    box(draw, CX-300, MID_Y-80, CX+300, MID_Y+40, "mdpdf web version", "mdpdf.whhite.com")
    frames.append((img, 800))

    # Frame 2 — add Docker + Puppeteer labels below
    img, draw = base()
    box(draw, CX-300, MID_Y-100, CX+300, MID_Y+20, "mdpdf web version", "mdpdf.whhite.com")
    arrow_down(draw, CX, MID_Y+20, MID_Y+56, color=RED)
    box(draw, CX-200, MID_Y+56, CX+200, MID_Y+116, "Docker  +  Puppeteer", "2x Chromium downloads", outline=RED, lcolor=RED)
    frames.append((img, 900))

    # Frame 3 — arrow pointing right to winmdPDF
    img, draw = base()
    LBX = CX - 480
    box(draw, LBX, MID_Y-80, LBX+340, MID_Y+40, "mdpdf web version", outline=BORDER)
    arrow_down(draw, LBX+170, MID_Y+40, MID_Y+76, color=RED)
    box(draw, LBX+60, MID_Y+76, LBX+280, MID_Y+136, "Docker  +  Puppeteer", "", outline=RED, lcolor=RED)
    arrow_right(draw, LBX+340, MID_Y-20, CX+80, color=GREEN)
    box(draw, CX+80, MID_Y-80, CX+440, MID_Y+40, "winmdPDF", "Electron desktop app", outline=ACCENT, lcolor=ACCENT)
    frames.append((img, 1000))

    # Frame 4 — final, checkmarks
    img, draw = base()
    box(draw, LBX, MID_Y-80, LBX+340, MID_Y+40, "mdpdf web version", outline=BORDER)
    arrow_down(draw, LBX+170, MID_Y+40, MID_Y+76, color=RED)
    box(draw, LBX+60, MID_Y+76, LBX+280, MID_Y+136, "Docker  +  Puppeteer", "", outline=RED, lcolor=RED)
    arrow_right(draw, LBX+340, MID_Y-20, CX+80, color=GREEN)
    box(draw, CX+80, MID_Y-80, CX+440, MID_Y+40, "winmdPDF", "Electron desktop app", outline=ACCENT, lcolor=ACCENT)
    checks = ["no Docker", "no server", "one Chromium"]
    ty = MID_Y - 44
    for c in checks:
        cw = draw.textbbox((0,0), "✓ " + c, font=FS)[2]
        draw.text((CX+80 + (360-cw)//2, ty), "✓ " + c, font=FS, fill=GREEN)
        ty += 28
    frames.append((img, 2200))

    return frames

# ─────────────────────────────────────────────────────────────────────────────
# Unique — Mermaid code → rendered diagram → "exports to PDF too"
# ─────────────────────────────────────────────────────────────────────────────
def unique_frames(W, H):
    frames = []
    PAD = 50
    TOP = 104; BOT = H - 68
    PH  = BOT - TOP
    PW  = (W - PAD * 3) // 2
    LX  = PAD; RX = PAD * 2 + PW

    CODE = [
        "```mermaid",
        "sequenceDiagram",
        "  User->>App: open doc",
        "  App->>PDF: export",
        "  PDF-->>User: file",
        "```",
    ]

    def base():
        img, draw = new_frame(W, H)
        header(draw, W, "What makes it different")
        footer(draw, W, H, "What makes it different")
        return img, draw

    # Frame 1 — Mermaid code block on left
    img, draw = base()
    draw.rounded_rectangle([LX, TOP, LX+PW, TOP+PH], radius=8, fill=SURFACE, outline=ACCENT)
    draw.text((LX+18, TOP+14), "mermaid diagram", font=FL, fill=ACCENT)
    ty = TOP + 52
    for line in CODE:
        draw.text((LX+18, ty), line, font=FM, fill=TEXT if not line.startswith("```") else MUTED)
        ty += 32
    draw.rounded_rectangle([RX, TOP, RX+PW, TOP+PH], radius=8, fill=SURFACE, outline=BORDER)
    draw.text((RX+18, TOP+14), "renders as...", font=FL, fill=MUTED)
    frames.append((img, 900))

    # Frame 2 — rendered diagram on right
    img, draw = base()
    draw.rounded_rectangle([LX, TOP, LX+PW, TOP+PH], radius=8, fill=SURFACE, outline=BORDER)
    draw.text((LX+18, TOP+14), "mermaid diagram", font=FL, fill=MUTED)
    ty = TOP + 52
    for line in CODE:
        draw.text((LX+18, ty), line, font=FM, fill=MUTED)
        ty += 32
    draw.rounded_rectangle([RX, TOP, RX+PW, TOP+PH], radius=8, fill=(20, 32, 54), outline=ACCENT)
    draw.text((RX+18, TOP+14), "renders as...", font=FL, fill=ACCENT)
    # Draw a simple sequence diagram
    DX = RX + 30; DW = PW - 60
    p1x = DX + DW//4; p2x = DX + 3*DW//4
    # Participants
    box(draw, p1x-40, TOP+50, p1x+40, TOP+84, "User", outline=ACCENT, fill=SURFACE)
    box(draw, p2x-40, TOP+50, p2x+40, TOP+84, "App",  outline=ACCENT, fill=SURFACE)
    # Lifelines
    draw.line([(p1x, TOP+84), (p1x, TOP+PH-40)], fill=BORDER, width=2)
    draw.line([(p2x, TOP+84), (p2x, TOP+PH-40)], fill=BORDER, width=2)
    # Message 1
    arrow_right(draw, p1x, TOP+120, p2x, color=TEXT)
    draw.text((p1x + (p2x-p1x)//2 - 40, TOP+100), "open doc", font=FS, fill=MUTED)
    # Message 2 — app to PDF (dashed look)
    p3x = p2x + 80
    box(draw, p3x-40, TOP+50, p3x+40, TOP+84, "PDF",  outline=MUTED, fill=SURFACE)
    draw.line([(p3x, TOP+84), (p3x, TOP+PH-40)], fill=BORDER, width=2)
    arrow_right(draw, p2x, TOP+165, p3x, color=TEXT)
    draw.text((p2x + (p3x-p2x)//2 - 22, TOP+145), "export", font=FS, fill=MUTED)
    # Return
    arrow_right(draw, p3x, TOP+210, p1x + (p3x-p1x), color=MUTED)
    draw.line([(p3x, TOP+210), (p1x, TOP+210)], fill=MUTED, width=2)
    draw.polygon([(p1x, TOP+210), (p1x+12, TOP+204), (p1x+12, TOP+216)], fill=MUTED)
    draw.text((p1x + (p3x-p1x)//2 - 14, TOP+192), "file", font=FS, fill=MUTED)
    frames.append((img, 1200))

    # Frame 3 — badge "exports to PDF exactly as shown"
    img, draw = base()
    draw.rounded_rectangle([LX, TOP, LX+PW, TOP+PH], radius=8, fill=SURFACE, outline=BORDER)
    draw.text((LX+18, TOP+14), "mermaid diagram", font=FL, fill=MUTED)
    ty = TOP + 52
    for line in CODE:
        draw.text((LX+18, ty), line, font=FM, fill=MUTED)
        ty += 32
    draw.rounded_rectangle([RX, TOP, RX+PW, TOP+PH], radius=8, fill=(20, 32, 54), outline=ACCENT)
    draw.text((RX+18, TOP+14), "renders as...", font=FL, fill=ACCENT)
    box(draw, p1x-40, TOP+50, p1x+40, TOP+84, "User", outline=ACCENT, fill=SURFACE)
    box(draw, p2x-40, TOP+50, p2x+40, TOP+84, "App",  outline=ACCENT, fill=SURFACE)
    draw.line([(p1x, TOP+84), (p1x, TOP+PH-40)], fill=BORDER, width=2)
    draw.line([(p2x, TOP+84), (p2x, TOP+PH-40)], fill=BORDER, width=2)
    arrow_right(draw, p1x, TOP+120, p2x, color=TEXT)
    draw.text((p1x + (p2x-p1x)//2 - 40, TOP+100), "open doc", font=FS, fill=MUTED)
    box(draw, p3x-40, TOP+50, p3x+40, TOP+84, "PDF",  outline=MUTED, fill=SURFACE)
    draw.line([(p3x, TOP+84), (p3x, TOP+PH-40)], fill=BORDER, width=2)
    arrow_right(draw, p2x, TOP+165, p3x, color=TEXT)
    draw.text((p2x + (p3x-p2x)//2 - 22, TOP+145), "export", font=FS, fill=MUTED)
    draw.line([(p3x, TOP+210), (p1x, TOP+210)], fill=MUTED, width=2)
    draw.polygon([(p1x, TOP+210), (p1x+12, TOP+204), (p1x+12, TOP+216)], fill=MUTED)
    draw.text((p1x + (p3x-p1x)//2 - 14, TOP+192), "file", font=FS, fill=MUTED)
    badge(draw, W//2, BOT - 28, "renders in PDF output too", bg=SURFACE, fg=GREEN)
    frames.append((img, 2200))

    return frames

# ─────────────────────────────────────────────────────────────────────────────
# Story — re-entering settings → winmdPDF remembers
# ─────────────────────────────────────────────────────────────────────────────
def story_frames(W, H):
    frames = []
    CX = W // 2
    TOP = 104; BOT = H - 68

    SETTINGS = [("Font", "Georgia"), ("Margins", "20mm"), ("Header", "My Name")]

    def base():
        img, draw = new_frame(W, H)
        header(draw, W, "Story")
        footer(draw, W, H, "Story")
        return img, draw

    def draw_settings_panel(draw, px, py, pw, ph, title, active=False, greyed=False):
        oc = ACCENT if active else (BORDER if not greyed else (40, 50, 66))
        fc = SURFACE if not greyed else (22, 32, 48)
        draw.rounded_rectangle([px, py, px+pw, py+ph], radius=8, fill=fc, outline=oc)
        tc = (ACCENT if active else (MUTED if greyed else TEXT))
        draw.text((px+16, py+12), title, font=FL, fill=tc)
        ty = py + 46
        for k, v in SETTINGS:
            kc = MUTED if greyed else MUTED
            vc = MUTED if greyed else TEXT
            draw.text((px+16, ty), k + ":", font=FS, fill=kc)
            draw.text((px+90, ty), v,    font=FS, fill=vc)
            ty += 26

    PW = 230; PH = 160
    PY = TOP + (BOT - TOP)//2 - PH//2

    # Frame 1 — Export 1, panel on left
    img, draw = base()
    draw_settings_panel(draw, CX-360, PY, PW, PH, "Export 1", active=True)
    tw = draw.textbbox((0,0), "re-enter settings...", font=FS)[2]
    draw.text((CX-360 + (PW-tw)//2, PY+PH+12), "re-enter settings...", font=FS, fill=RED)
    frames.append((img, 800))

    # Frame 2 — Export 2, second panel
    img, draw = base()
    draw_settings_panel(draw, CX-500, PY, PW, PH, "Export 1", greyed=True)
    draw_settings_panel(draw, CX-240, PY, PW, PH, "Export 2", active=True)
    tw = draw.textbbox((0,0), "re-enter settings...", font=FS)[2]
    draw.text((CX-240 + (PW-tw)//2, PY+PH+12), "re-enter settings...", font=FS, fill=RED)
    frames.append((img, 900))

    # Frame 3 — Export 3, third panel, clear frustration
    img, draw = base()
    draw_settings_panel(draw, CX-500, PY, PW, PH, "Export 1", greyed=True)
    draw_settings_panel(draw, CX-240, PY, PW, PH, "Export 2", greyed=True)
    draw_settings_panel(draw, CX+20,  PY, PW, PH, "Export 3", active=True)
    tw = draw.textbbox((0,0), "again?", font=FS)[2]
    draw.text((CX+20 + (PW-tw)//2, PY+PH+12), "again?", font=FS, fill=RED)
    frames.append((img, 900))

    # Frame 4 — winmdPDF: settings saved once, persist
    img, draw = base()
    BX = CX - PW//2
    draw_settings_panel(draw, BX, PY-20, PW, PH, "winmdPDF", active=True)
    sw = draw.textbbox((0,0), "✓  settings saved automatically", font=FS)[2]
    draw.text((BX + (PW-sw)//2, PY+PH), "✓  settings saved automatically", font=FS, fill=GREEN)
    badge(draw, CX, PY + PH + 54, "open app, export, done", bg=SURFACE, fg=ACCENT)
    frames.append((img, 2400))

    return frames

# ─────────────────────────────────────────────────────────────────────────────
# Assemble all GIFs — LinkedIn (1200x628) and Twitter (1200x675)
# ─────────────────────────────────────────────────────────────────────────────
ANIMATIONS = {
    "eli5":      eli5_frames,
    "technical": technical_frames,
    "why-built": why_frames,
    "unique":    unique_frames,
    "story":     story_frames,
}

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)

    for slug, fn in ANIMATIONS.items():
        print(f"\n{slug}")
        for platform, (W, H) in [("linkedin", (1200, 628)), ("twitter", (1200, 675))]:
            frames_ms = [(img, ms) for img, ms in fn(W, H)]
            save_gif(frames_ms, f"{platform}-{slug}.gif")

    print("\nDone. Files in posts/gifs/")
