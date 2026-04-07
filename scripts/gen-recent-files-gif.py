"""
mdPDF demo GIF — Recent Files & Open/Drag-Drop feature showcase.
Journey: idle (Open button) → open file → recent panel appears → drag-drop overlay → 2 recents
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ── Dimensions & palette ─────────────────────────────────────────────────────
W, H = 900, 560
SIDEBAR_W  = 52
EDITOR_W   = 380
PREVIEW_W  = W - SIDEBAR_W - EDITOR_W

BG_APP     = (3,   7,  18)
BG_HEADER  = (15,  23,  42)
BG_EDITOR  = (13,  20,  36)
BG_PREVIEW = (255, 255, 255)
BG_SIDEBAR = (255, 255, 255)
BG_TOOLBAR = (13,  20,  36)
BG_RECENT  = (10,  14,  28)

TXT_EDITOR  = (148, 163, 184)
TXT_PREVIEW = (30,  41,  59)
TXT_MUTED   = (100, 116, 139)
TXT_WHITE   = (255, 255, 255)

ACCENT  = (99,  102, 241)
ACCENT2 = (167, 139, 250)
ACCENT3 = (232, 121, 249)

BORDER_D = (30, 41, 59)
BORDER_L = (226, 232, 240)

HEADING_COLOR = (99, 102, 241)
CODE_BG       = (241, 245, 249)
CODE_TXT      = (30,  41,  59)

FONT_DIR = "C:/Windows/Fonts/"

def font(name, size):
    for path in [FONT_DIR + name, FONT_DIR + "arial.ttf"]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

F_UI_XS  = font("segoeui.ttf",  10)
F_UI_SM  = font("segoeui.ttf",  11)
F_UI_MD  = font("segoeui.ttf",  13)
F_UI_B   = font("segoeuib.ttf", 13)
F_UI_LG  = font("segoeuib.ttf", 15)
F_MONO   = font("CascadiaCode.ttf", 11)
F_MONO_S = font("CascadiaCode.ttf", 10)
F_H1     = font("segoeuib.ttf", 18)
F_H2     = font("segoeuib.ttf", 14)
F_SERIF  = font("georgia.ttf",  22)
F_SERIF_S= font("georgia.ttf",  16)

# ── Helpers ───────────────────────────────────────────────────────────────────
def rr(draw, xy, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(xy, r, fill=fill, outline=outline, width=width)

def text_w(draw, text, fnt):
    return draw.textbbox((0, 0), text, font=fnt)[2]

def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# ── Components ────────────────────────────────────────────────────────────────

def draw_gradient_bar(img, y=0, h=3):
    for x in range(W):
        t = x / (W - 1)
        c = lerp_color(ACCENT, ACCENT2, t * 2) if t < 0.5 else lerp_color(ACCENT2, ACCENT3, (t - 0.5) * 2)
        for dy in range(h):
            img.putpixel((x, y + dy), c)

def draw_header(draw, img, open_hover=False, exporting=False):
    draw.rectangle([(0, 3), (W - 1, 54)], fill=BG_HEADER)
    draw.line([(0, 54), (W, 54)], fill=BORDER_D, width=1)

    # Logo
    xi = 16
    draw.text((xi, 18), "md", font=F_SERIF, fill=TXT_WHITE)
    ax = xi + 34
    draw.line([(ax, 30), (ax + 22, 30)], fill=ACCENT, width=2)
    draw.line([(ax + 16, 25), (ax + 22, 30), (ax + 16, 35)], fill=ACCENT, width=2)
    draw.text((ax + 28, 18), "PDF", font=F_SERIF_S, fill=TXT_WHITE)

    # Open button
    ux = W - 200
    btn_bg = (30, 40, 65) if open_hover else None
    btn_border = (90, 100, 160) if open_hover else (60, 70, 90)
    rr(draw, [(ux, 17), (ux + 72, 39)], 4, fill=btn_bg, outline=btn_border, width=1)
    # folder icon (simplified)
    draw.rectangle([(ux + 8, 24), (ux + 19, 33)], outline=(100 if not open_hover else 160, 120, 200), width=1)
    draw.rectangle([(ux + 8, 22), (ux + 14, 25)], fill=(100 if not open_hover else 160, 120, 200))
    txt_col = (200, 210, 230) if open_hover else TXT_MUTED
    draw.text((ux + 24, 22), "Open", font=F_UI_XS, fill=txt_col)

    # Export button
    ex = W - 116
    fill = (55, 48, 163) if exporting else (79, 70, 229)
    label = "Exporting…" if exporting else "Export PDF"
    rr(draw, [(ex, 17), (ex + 98, 39)], 4, fill=fill)
    draw.text((ex + 8, 22), label, font=F_UI_XS, fill=TXT_WHITE)

def draw_recent_panel(draw, files=None, collapsed=False):
    """Recent files strip below the header."""
    panel_y0 = 55
    panel_y1 = 55 + 28 + (0 if collapsed else 28)
    draw.rectangle([(0, panel_y0), (W, panel_y1)], fill=BG_RECENT)
    draw.line([(0, panel_y1), (W, panel_y1)], fill=(40, 40, 80), width=1)

    # Chevron
    cy = panel_y0 + 14
    if collapsed:
        draw.polygon([(10, cy - 4), (10, cy + 4), (15, cy)], fill=ACCENT)
    else:
        draw.polygon([(10, cy - 2), (14, cy + 4), (18, cy - 2)], fill=ACCENT)

    draw.text((22, panel_y0 + 8), "RECENT", font=F_UI_XS, fill=TXT_MUTED)
    if files:
        count_str = str(len(files))
        draw.text((22 + text_w(draw, "RECENT", F_UI_XS) + 6, panel_y0 + 8), count_str, font=F_UI_XS, fill=(70, 80, 100))

    if not collapsed and files:
        chip_x = 16
        chip_y = panel_y0 + 30
        for i, (fname, age, hovered) in enumerate(files):
            chip_w = 8 + text_w(draw, fname, F_UI_SM) + 8 + text_w(draw, age, F_UI_XS) + 6 + 16
            chip_w = min(chip_w, 190)
            bg = (40, 50, 90) if hovered else (20, 26, 46)
            border = (80, 90, 180) if hovered else (40, 50, 75)
            rr(draw, [(chip_x, chip_y), (chip_x + chip_w, chip_y + 22)], 4, fill=bg, outline=border, width=1)
            # doc icon
            draw.rectangle([(chip_x + 6, chip_y + 5), (chip_x + 13, chip_y + 17)], outline=ACCENT, width=1)
            draw.line([(chip_x + 8, chip_y + 9), (chip_x + 11, chip_y + 9)], fill=ACCENT, width=1)
            draw.line([(chip_x + 8, chip_y + 12), (chip_x + 11, chip_y + 12)], fill=ACCENT, width=1)
            # filename
            fn_x = chip_x + 18
            draw.text((fn_x, chip_y + 5), fname[:18], font=F_UI_SM, fill=(200, 210, 230))
            age_x = fn_x + text_w(draw, fname[:18], F_UI_SM) + 4
            draw.text((age_x, chip_y + 6), age, font=F_UI_XS, fill=(70, 80, 100))
            chip_x += chip_w + 8

def draw_panel_labels(draw, recent_h=0):
    y0 = 55 + recent_h
    y1 = y0 + 32

    draw.rectangle([(0, y0), (SIDEBAR_W, y1)], fill=BG_SIDEBAR)
    draw.line([(SIDEBAR_W, y0), (SIDEBAR_W, y1)], fill=BORDER_L, width=1)
    draw.line([(0, y1), (SIDEBAR_W, y1)], fill=BORDER_L, width=1)

    ex0, ex1 = SIDEBAR_W, SIDEBAR_W + EDITOR_W
    draw.rectangle([(ex0, y0), (ex1, y1)], fill=BG_EDITOR)
    draw.text((ex0 + 16, y0 + 10), "MARKDOWN", font=F_UI_XS, fill=TXT_MUTED)
    draw.line([(ex0, y1), (ex1, y1)], fill=BORDER_D, width=1)
    draw.line([(ex1, y0), (ex1, y1)], fill=BORDER_D, width=1)

    px0 = ex1
    draw.rectangle([(px0, y0), (W, y1)], fill=BG_PREVIEW)
    draw.text((px0 + 16, y0 + 10), "PREVIEW", font=F_UI_XS, fill=(148, 163, 184))
    draw.line([(px0, y1), (W, y1)], fill=BORDER_L, width=1)

def draw_sidebar(draw, recent_h=0):
    y0 = 55 + recent_h + 32
    draw.rectangle([(0, y0), (SIDEBAR_W, H)], fill=BG_SIDEBAR)
    draw.line([(SIDEBAR_W, y0), (SIDEBAR_W, H)], fill=BORDER_L, width=1)
    ax = SIDEBAR_W - 14
    ay = y0 + 22
    draw.polygon([(ax, ay), (ax + 8, ay + 6), (ax + 8, ay - 6)], fill=(200, 210, 220))

def draw_toolbar(draw, recent_h=0):
    editor_top = 55 + recent_h + 32
    y0, y1 = editor_top, editor_top + 34
    x0, x1 = SIDEBAR_W, SIDEBAR_W + EDITOR_W
    draw.rectangle([(x0, y0), (x1, y1)], fill=BG_TOOLBAR)
    draw.line([(x0, y1), (x1, y1)], fill=BORDER_D, width=1)

    alpha = (148, 163, 184)
    dim   = (60,  72,  90)
    bx = x0 + 10
    for ic in ["B", "I", "U", "S"]:
        fnt = F_UI_B if ic == "B" else F_UI_SM
        draw.text((bx + 2, y0 + 9), ic, font=fnt, fill=dim)
        bx += 26
    draw.line([(bx + 4, y0 + 9), (bx + 4, y1 - 9)], fill=(40, 55, 75), width=1)
    bx += 12
    draw.text((bx, y0 + 9), "A", font=F_UI_B, fill=dim)
    bx += 18
    draw.text((bx, y0 + 9), "H", font=F_UI_B, fill=dim)

def draw_editor(draw, lines, recent_h=0):
    editor_top = 55 + recent_h + 32 + 34
    x0, x1 = SIDEBAR_W, SIDEBAR_W + EDITOR_W
    draw.rectangle([(x0, editor_top), (x1, H)], fill=BG_EDITOR)
    ty = editor_top + 14
    for line in lines:
        if ty > H - 10:
            break
        if line.startswith("# "):
            clr = (161, 161, 251)
        elif line.startswith("## "):
            clr = (147, 153, 240)
        elif line.startswith("```"):
            clr = (100, 116, 139)
        else:
            clr = TXT_EDITOR
        txt = line
        while txt and text_w(draw, txt, F_MONO_S) > EDITOR_W - 30:
            txt = txt[:-1]
        draw.text((x0 + 20, ty), txt, font=F_MONO_S, fill=clr)
        ty += 16

def draw_preview_default(draw, recent_h=0):
    x0 = SIDEBAR_W + EDITOR_W
    y0 = 55 + recent_h + 32
    draw.rectangle([(x0, y0), (W, H)], fill=BG_PREVIEW)
    draw.line([(x0, y0), (x0, H)], fill=BORDER_L, width=1)
    tx = x0 + 22
    ty = y0 + 16
    draw.text((tx, ty), "Welcome to mdPDF", font=F_H1, fill=HEADING_COLOR)
    ty += 30
    draw.text((tx, ty), "Start writing Markdown on the left,", font=F_UI_MD, fill=TXT_PREVIEW)
    ty += 20
    draw.text((tx, ty), "your preview appears here instantly.", font=F_UI_MD, fill=TXT_PREVIEW)
    ty += 28
    draw.text((tx, ty), "What's supported", font=F_H2, fill=HEADING_COLOR)
    ty += 22
    for bullet in ["Bold, italic, strikethrough, `code`",
                   "Tables, task lists, blockquotes",
                   "Mermaid diagrams (flowcharts, …)"]:
        draw.ellipse([(tx + 3, ty + 5), (tx + 7, ty + 9)], fill=ACCENT)
        draw.text((tx + 14, ty), bullet, font=F_UI_SM, fill=TXT_PREVIEW)
        ty += 18

def draw_preview_doc(draw, title, recent_h=0):
    """Preview with a loaded document."""
    x0 = SIDEBAR_W + EDITOR_W
    y0 = 55 + recent_h + 32
    draw.rectangle([(x0, y0), (W, H)], fill=BG_PREVIEW)
    draw.line([(x0, y0), (x0, H)], fill=BORDER_L, width=1)
    tx = x0 + 22
    ty = y0 + 16
    draw.text((tx, ty), title, font=F_H1, fill=HEADING_COLOR)
    ty += 28
    lines = [
        "This document was opened from disk.",
        "",
        "Edit it on the left, export as PDF",
        "when you're ready.",
        "",
    ]
    for l in lines:
        draw.text((tx, ty), l, font=F_UI_SM, fill=TXT_PREVIEW)
        ty += 18
    draw.text((tx, ty), "Features", font=F_H2, fill=HEADING_COLOR)
    ty += 22
    for bullet in ["Live preview", "Style settings", "Diagram support"]:
        draw.ellipse([(tx + 3, ty + 5), (tx + 7, ty + 9)], fill=ACCENT)
        draw.text((tx + 14, ty), bullet, font=F_UI_SM, fill=TXT_PREVIEW)
        ty += 18

def draw_drag_overlay(draw, recent_h=0):
    """Drag-over overlay on editor column."""
    editor_top = 55 + recent_h + 32
    x0, x1 = SIDEBAR_W, SIDEBAR_W + EDITOR_W

    # Tinted background
    overlay = Image.new("RGBA", (x1 - x0, H - editor_top), (60, 70, 180, 30))
    # We draw directly as a translucent rect approximation
    draw.rectangle([(x0, editor_top), (x1, H)], fill=(18, 22, 50))

    # Dashed border
    dash = 8
    gap  = 5
    for x in range(x0 + 4, x1 - 4, dash + gap):
        draw.line([(x, editor_top + 4), (min(x + dash, x1 - 4), editor_top + 4)], fill=ACCENT, width=2)
        draw.line([(x, H - 4), (min(x + dash, x1 - 4), H - 4)], fill=ACCENT, width=2)
    for y in range(editor_top + 4, H - 4, dash + gap):
        draw.line([(x0 + 4, y), (x0 + 4, min(y + dash, H - 4))], fill=ACCENT, width=2)
        draw.line([(x1 - 4, y), (x1 - 4, min(y + dash, H - 4))], fill=ACCENT, width=2)

    # Icon
    cx = x0 + EDITOR_W // 2
    cy = editor_top + (H - editor_top) // 2 - 24
    # Down arrow into folder
    draw.line([(cx, cy - 18), (cx, cy + 8)], fill=ACCENT, width=3)
    draw.polygon([(cx - 8, cy + 2), (cx + 8, cy + 2), (cx, cy + 14)], fill=ACCENT)
    draw.rectangle([(cx - 18, cy + 14), (cx + 18, cy + 28)], outline=ACCENT, width=2)

    label = "Drop to open"
    lw = text_w(draw, label, F_UI_B)
    draw.text((cx - lw // 2, cy + 38), label, font=F_UI_B, fill=(160, 170, 255))
    sub = ".md  ·  .markdown  ·  .txt"
    sw = text_w(draw, sub, F_UI_XS)
    draw.text((cx - sw // 2, cy + 58), sub, font=F_UI_XS, fill=(80, 90, 140))

# ── make_frame ────────────────────────────────────────────────────────────────
def make_frame(
    editor_lines=None,
    open_hover=False,
    show_recent=False,
    recent_files=None,
    drag_over=False,
    preview_mode="default",
    preview_title="",
    exporting=False,
):
    img  = Image.new("RGB", (W, H), BG_APP)
    draw = ImageDraw.Draw(img)

    recent_h = 56 if show_recent else 0

    draw_gradient_bar(img)
    draw_header(draw, img, open_hover=open_hover, exporting=exporting)

    if show_recent:
        draw_recent_panel(draw, files=recent_files or [])

    draw_panel_labels(draw, recent_h=recent_h)
    draw_sidebar(draw, recent_h=recent_h)
    draw_toolbar(draw, recent_h=recent_h)

    if drag_over:
        draw_editor(draw, editor_lines or [], recent_h=recent_h)
        draw_drag_overlay(draw, recent_h=recent_h)
    else:
        draw_editor(draw, editor_lines or [], recent_h=recent_h)

    if preview_mode == "doc":
        draw_preview_doc(draw, preview_title, recent_h=recent_h)
    else:
        draw_preview_default(draw, recent_h=recent_h)

    return img

# ── Content ───────────────────────────────────────────────────────────────────
LINES_WELCOME = [
    "# Welcome to mdPDF",
    "",
    "Start writing **Markdown** on the left,",
    "your preview appears here instantly.",
    "",
    "## What's supported",
    "",
    "- Bold, italic, ~~strike~~, `code`",
    "- Tables, task lists, blockquotes",
    "- Mermaid diagrams",
]

LINES_REPORT = [
    "# Q1 Report",
    "",
    "This document was opened from disk.",
    "",
    "## Summary",
    "",
    "- Revenue up 18% quarter over quarter",
    "- Onboarding improved significantly",
    "- Engineering velocity increased",
]

LINES_NOTES = [
    "# Meeting Notes",
    "",
    "Project kickoff — Apr 7 2026",
    "",
    "## Action items",
    "",
    "- [ ] Finalize scope",
    "- [ ] Assign owners",
    "- [x] Set timeline",
]

RECENT_ONE = [("q1-report.md", "just now", False)]
RECENT_TWO = [("q1-report.md", "2m ago", False), ("meeting-notes.md", "just now", True)]

# ── Scenes ────────────────────────────────────────────────────────────────────
scenes = [
    # 1. Idle — Open button visible, no recent panel
    dict(ms=1500, state=dict(editor_lines=LINES_WELCOME, preview_mode="default")),

    # 2. Hover over Open button
    dict(ms=600,  state=dict(editor_lines=LINES_WELCOME, preview_mode="default", open_hover=True)),

    # 3. File opened — recent panel appears, preview updates
    dict(ms=400,  state=dict(editor_lines=LINES_REPORT, preview_mode="doc", preview_title="Q1 Report",
                              show_recent=True, recent_files=RECENT_ONE)),

    # 4. Hold — user reads the file
    dict(ms=1500, state=dict(editor_lines=LINES_REPORT, preview_mode="doc", preview_title="Q1 Report",
                              show_recent=True, recent_files=RECENT_ONE)),

    # 5. Drag a second file over editor
    dict(ms=800,  state=dict(editor_lines=LINES_REPORT, preview_mode="doc", preview_title="Q1 Report",
                              show_recent=True, recent_files=RECENT_ONE, drag_over=True)),

    # 6. Drop — second file loads, recent panel shows 2 chips
    dict(ms=400,  state=dict(editor_lines=LINES_NOTES, preview_mode="doc", preview_title="Meeting Notes",
                              show_recent=True, recent_files=RECENT_TWO)),

    # 7. Hold — 2 recents visible
    dict(ms=1800, state=dict(editor_lines=LINES_NOTES, preview_mode="doc", preview_title="Meeting Notes",
                              show_recent=True, recent_files=RECENT_TWO)),

    # 8. Click first chip (q1-report) — re-opens it, it jumps to top
    dict(ms=400,  state=dict(editor_lines=LINES_REPORT, preview_mode="doc", preview_title="Q1 Report",
                              show_recent=True,
                              recent_files=[("q1-report.md", "just now", False), ("meeting-notes.md", "3m ago", False)])),

    # 9. Hold
    dict(ms=1200, state=dict(editor_lines=LINES_REPORT, preview_mode="doc", preview_title="Q1 Report",
                              show_recent=True,
                              recent_files=[("q1-report.md", "just now", False), ("meeting-notes.md", "3m ago", False)])),

    # 10. Loop back to idle
    dict(ms=800,  state=dict(editor_lines=LINES_WELCOME, preview_mode="default")),
]

# ── Render ────────────────────────────────────────────────────────────────────
print("Rendering frames…")
frames    = [make_frame(**s["state"]) for s in scenes]
durations = [s["ms"] for s in scenes]

print("Quantizing…")
quant = [f.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for f in frames]

out = "recent-files-demo.gif"
print(f"Saving {out}…")
quant[0].save(
    out,
    save_all=True,
    append_images=quant[1:],
    duration=durations,
    loop=0,
    optimize=True,
)

size_mb = os.path.getsize(out) / 1_000_000
print(f"Done → {out}  ({size_mb:.2f} MB, {len(frames)} frames)")

if size_mb > 5:
    print("Over 5 MB budget — re-quantizing to 64 colors…")
    quant64 = [f.quantize(colors=64, method=Image.Quantize.MEDIANCUT) for f in frames]
    quant64[0].save(
        out, save_all=True, append_images=quant64[1:],
        duration=durations, loop=0, optimize=True,
    )
    size_mb = os.path.getsize(out) / 1_000_000
    print(f"Re-saved → {size_mb:.2f} MB")
