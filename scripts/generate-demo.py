"""
winmdPDF demo GIF generator
Renders a fake-but-realistic demo of the Markdown → PDF editor flow.
Output: demo.gif (900x580, <2 MB)
"""

from PIL import Image, ImageDraw, ImageFont
import os, math

# ── Dimensions ─────────────────────────────────────────────────────────────────
W, H = 900, 580
SIDEBAR_W   = 180   # style sidebar
EDITOR_W    = 360   # editor panel
PREVIEW_W   = W - SIDEBAR_W - EDITOR_W  # 360

HEADER_H    = 52
LABEL_H     = 32
TOOLBAR_H   = 34
TOP_STRIP_H = 3

CONTENT_TOP = TOP_STRIP_H + HEADER_H + LABEL_H   # 87
EDITOR_TOP  = CONTENT_TOP + TOOLBAR_H             # 121

# ── Palette ────────────────────────────────────────────────────────────────────
APP_BG          = (15, 23, 42)      # #0f172a  slate-950
HEADER_BG       = (30, 41, 59)      # #1e293b  slate-900
EDITOR_BG       = (13, 20, 36)      # #0d1424
PREVIEW_BG      = (255, 255, 255)   # white
SIDEBAR_BG      = (255, 255, 255)   # white
TOOLBAR_BG      = (13, 20, 36)      # same as editor

# Accent gradient colours (approximated as flat colours per usage)
ACCENT_1        = (99, 102, 241)    # #6366f1  indigo-500
ACCENT_2        = (139, 92, 246)    # #8b5cf6  violet-500
ACCENT_3        = (217, 70, 239)    # #d946ef  fuchsia-500

# Text colours
TEXT_LIGHT      = (241, 245, 249)   # #f1f5f9  slate-100
TEXT_MUTED      = (148, 163, 184)   # #94a3b8  slate-400
TEXT_DARK       = (30, 41, 59)      # #1e293b  on white
TEXT_FAINT      = (100, 116, 139)   # #64748b  slate-500
BORDER_DARK     = (255, 255, 255, 15)  # rgba(255,255,255,0.06) – approximate
BORDER_LIGHT    = (226, 232, 240)   # #e2e8f0

# Editor syntax colours
SYN_HASH        = (129, 140, 248)   # #818cf8  indigo-400  (# sigil)
SYN_HEADING     = (224, 231, 255)   # #e0e7ff  indigo-100  (heading text)
SYN_PLAIN       = (148, 163, 184)   # #94a3b8  slate-400
SYN_BOLD_MARK   = (196, 181, 253)   # #c4b5fd  violet-300
SYN_CODE_BG     = (23, 32, 52)
SYN_CODE_TEXT   = (110, 231, 183)   # emerald-300
SYN_TABLE_PIPE  = (99, 102, 241)    # indigo

# Preview colours
PREV_H1         = (15, 23, 42)      # near-black for big headings
PREV_H2         = (30, 41, 59)
PREV_BODY       = (51, 65, 85)      # slate-700
PREV_TABLE_HDR  = (241, 245, 249)   # slate-100
PREV_TABLE_BDR  = (226, 232, 240)
PREV_TABLE_EVEN = (248, 250, 252)   # slate-50
PREV_LINK       = (99, 102, 241)    # indigo

# ── Font dir ───────────────────────────────────────────────────────────────────
FONT_DIR = "C:/Windows/Fonts/"

def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for f in [name, "segoeui.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(FONT_DIR + f, size)
        except Exception:
            pass
    return ImageFont.load_default()

def mono(name: str, size: int) -> ImageFont.FreeTypeFont:
    for f in [name, "consolab.ttf", "consola.ttf", "cour.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(FONT_DIR + f, size)
        except Exception:
            pass
    return ImageFont.load_default()

# Pre-load fonts
F_UI_SM    = font("segoeui.ttf", 10)
F_UI_XS    = font("segoeui.ttf", 9)
F_UI       = font("segoeui.ttf", 12)
F_UI_MD    = font("segoeui.ttf", 13)
F_UI_LG    = font("segoeuib.ttf", 15)
F_LOGO     = font("georgiab.ttf", 18)   # serif italic fallback
F_LOGO2    = font("georgia.ttf", 18)
F_MONO     = mono("consola.ttf", 12)
F_MONO_SM  = mono("consola.ttf", 11)
F_PREV_H1  = font("segoeuib.ttf", 22)
F_PREV_H2  = font("segoeuib.ttf", 16)
F_PREV_H3  = font("segoeuib.ttf", 13)
F_PREV_BODY= font("segoeui.ttf", 12)
F_PREV_SM  = font("segoeui.ttf", 11)
F_BTN      = font("segoeuib.ttf", 11)


# ── Gradient helpers ──────────────────────────────────────────────────────────
def draw_h_gradient(img: Image.Image, x0: int, y0: int, x1: int, y1: int,
                    c_left: tuple, c_right: tuple):
    """Draw a horizontal linear gradient rectangle."""
    draw = ImageDraw.Draw(img)
    width = x1 - x0
    if width <= 0:
        return
    for px in range(width):
        t = px / max(width - 1, 1)
        r = int(c_left[0] + (c_right[0] - c_left[0]) * t)
        g = int(c_left[1] + (c_right[1] - c_left[1]) * t)
        b = int(c_left[2] + (c_right[2] - c_left[2]) * t)
        draw.line([(x0 + px, y0), (x0 + px, y1)], fill=(r, g, b))


def draw_btn_gradient(img: Image.Image, x0: int, y0: int, x1: int, y1: int,
                      radius: int = 6, label: str = "Export PDF",
                      label_font=None, spinner: bool = False):
    """Draw the purple gradient Export PDF button."""
    draw = ImageDraw.Draw(img)
    draw_h_gradient(img, x0, y0, x1, y1, ACCENT_1, ACCENT_2)
    # Clip corners with rounded rect outline trick: redraw BG over corners
    # (Simple approach: draw a rounded rect with same gradient isn't trivial,
    #  so we draw the full rect then mask corners with app BG colour)
    corner = HEADER_BG
    r = radius
    draw.rectangle([x0, y0, x0 + r, y0 + r], fill=corner)
    draw.rectangle([x1 - r, y0, x1, y0 + r], fill=corner)
    draw.rectangle([x0, y1 - r, x0 + r, y1], fill=corner)
    draw.rectangle([x1 - r, y1 - r, x1, y1], fill=corner)
    # Redraw gradient in the arcs
    draw_h_gradient(img, x0, y0, x1, y1 // 1, ACCENT_1, ACCENT_2)
    # Actually just use rounded_rectangle for simplicity
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # draw gradient pixels are already there; add rounded_rectangle as mask
    od.rounded_rectangle([x0, y0, x1, y1], radius=radius,
                         fill=None, outline=(255, 255, 255, 30), width=1)
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"),
              box=(0, 0))

    if label_font is None:
        label_font = F_BTN
    lbl = "Generating…" if spinner else label
    bbox = label_font.getbbox(lbl)
    lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cx = (x0 + x1) // 2 - lw // 2
    cy = (y0 + y1) // 2 - lh // 2
    draw.text((cx, cy), lbl, font=label_font, fill=(255, 255, 255))

    if spinner:
        # small arc indicator
        draw.arc([x1 - 20, y0 + 4, x1 - 8, y1 - 4], start=0, end=270,
                 fill=(255, 255, 255, 180), width=2)


# ── Component draw functions ──────────────────────────────────────────────────

def draw_top_strip(draw: ImageDraw.ImageDraw, img: Image.Image):
    """3px top accent strip with gradient."""
    draw_h_gradient(img, 0, 0, W, TOP_STRIP_H, ACCENT_1, ACCENT_3)


def draw_header(draw: ImageDraw.ImageDraw, img: Image.Image,
                export_state: str = "idle"):
    """Header bar with logo + buttons."""
    y0, y1 = TOP_STRIP_H, TOP_STRIP_H + HEADER_H
    draw.rectangle([0, y0, W, y1], fill=HEADER_BG)
    draw.line([(0, y1), (W, y1)], fill=(255, 255, 255, 15), width=1)

    # Logo: "md → PDF"
    lx = 20
    ly = y0 + (HEADER_H - 20) // 2
    draw.text((lx, ly), "md", font=F_LOGO2, fill=TEXT_LIGHT)
    # Arrow →
    ax = lx + F_LOGO2.getbbox("md")[2] + 6
    draw.text((ax, ly + 2), "→", font=F_UI_MD, fill=(129, 140, 248))
    px = ax + F_UI_MD.getbbox("→")[2] + 6
    draw.text((px, ly), "PDF", font=F_LOGO, fill=TEXT_LIGHT)

    # Upload .md button
    ubx0 = W - 200
    ubx1 = ubx0 + 90
    uby0 = y0 + 13
    uby1 = uby0 + 26
    draw.rounded_rectangle([ubx0, uby0, ubx1, uby1], radius=5,
                           fill=None, outline=(255, 255, 255, 25))
    draw.rounded_rectangle([ubx0, uby0, ubx1, uby1], radius=5,
                           fill=(30, 41, 59), outline=(60, 70, 90))
    draw.text((ubx0 + 10, uby0 + 7), "↑ Upload .md", font=F_UI_SM, fill=TEXT_MUTED)

    # Export PDF button
    ebx0 = W - 102
    ebx1 = W - 16
    eby0 = y0 + 13
    eby1 = eby0 + 26
    spinner = (export_state == "generating")
    draw_btn_gradient(img, ebx0, eby0, ebx1, eby1,
                      radius=5, label="Export PDF",
                      label_font=F_BTN, spinner=spinner)


def draw_panel_labels(draw: ImageDraw.ImageDraw):
    """The thin label row under header."""
    y0, y1 = TOP_STRIP_H + HEADER_H, TOP_STRIP_H + HEADER_H + LABEL_H

    # Sidebar label area (white)
    draw.rectangle([0, y0, SIDEBAR_W, y1], fill=SIDEBAR_BG)
    draw.line([(SIDEBAR_W, y0), (SIDEBAR_W, y1)], fill=BORDER_LIGHT, width=1)
    draw.line([(0, y1), (SIDEBAR_W, y1)], fill=BORDER_LIGHT, width=1)

    # Editor label
    ex0, ex1 = SIDEBAR_W, SIDEBAR_W + EDITOR_W
    draw.rectangle([ex0, y0, ex1, y1], fill=(15, 23, 42))
    draw.line([(ex1, y0), (ex1, y1)], fill=(255, 255, 255, 15), width=1)
    draw.line([(ex0, y1), (ex1, y1)], fill=(255, 255, 255, 15), width=1)
    # "MARKDOWN" label
    draw.text((ex0 + 20, y0 + 10), "MARKDOWN", font=F_UI_XS, fill=TEXT_FAINT)

    # Preview label
    px0, px1 = SIDEBAR_W + EDITOR_W, W
    draw.rectangle([px0, y0, px1, y1], fill=PREVIEW_BG)
    draw.line([(px0, y1), (px1, y1)], fill=BORDER_LIGHT, width=1)
    draw.text((px0 + 20, y0 + 10), "PREVIEW", font=F_UI_XS, fill=(148, 163, 184))
    draw.text((px1 - 120, y0 + 10), "Preview is approximate",
              font=F_UI_XS, fill=(203, 213, 225))


def draw_format_toolbar(draw: ImageDraw.ImageDraw):
    """Thin format toolbar above editor."""
    y0 = CONTENT_TOP
    y1 = y0 + TOOLBAR_H
    x0 = SIDEBAR_W
    x1 = SIDEBAR_W + EDITOR_W
    draw.rectangle([x0, y0, x1, y1], fill=TOOLBAR_BG)
    draw.line([(x0, y1), (x1, y1)], fill=(255, 255, 255, 15), width=1)

    # Toolbar buttons: Undo | B I U S | A H | Font Size | Diagram
    bx = x0 + 10
    by_center = (y0 + y1) // 2

    def small_btn(label: str, bx: int):
        bw, bh = 26, 22
        bby = by_center - bh // 2
        draw.rounded_rectangle([bx, bby, bx + bw, bby + bh],
                               radius=3, fill=(30, 41, 59))
        bb = F_UI_SM.getbbox(label)
        lw = bb[2] - bb[0]
        draw.text((bx + (bw - lw) // 2, bby + 5), label,
                  font=F_UI_SM, fill=TEXT_MUTED)
        return bx + bw + 4

    def divider(bx: int):
        draw.line([(bx + 3, by_center - 8), (bx + 3, by_center + 8)],
                  fill=(255, 255, 255, 25), width=1)
        return bx + 10

    bx = small_btn("↩", bx)
    bx = divider(bx)
    bx = small_btn("B", bx)
    bx = small_btn("I", bx)
    bx = small_btn("U", bx)
    bx = small_btn("S̶", bx)
    bx = divider(bx)
    bx = small_btn("A", bx)
    bx = small_btn("H", bx)
    bx = divider(bx)

    # Font/Size dropdowns
    for lbl in ["Font ▾", "Size ▾"]:
        dw = 54
        dby = by_center - 11
        draw.rounded_rectangle([bx, dby, bx + dw, dby + 22],
                               radius=3, fill=(30, 41, 59),
                               outline=(60, 70, 90))
        draw.text((bx + 6, dby + 6), lbl, font=F_UI_XS, fill=TEXT_MUTED)
        bx += dw + 4

    bx = divider(bx)
    # Diagram button
    dw = 62
    dby = by_center - 11
    draw.rounded_rectangle([bx, dby, bx + dw, dby + 22],
                           radius=3, fill=(30, 41, 59),
                           outline=(60, 70, 90))
    draw.text((bx + 8, dby + 6), "⎇ Diagram", font=F_UI_XS, fill=TEXT_MUTED)


def draw_sidebar(draw: ImageDraw.ImageDraw):
    """Style sidebar."""
    x0, x1 = 0, SIDEBAR_W
    y0, y1 = CONTENT_TOP, H
    draw.rectangle([x0, y0, x1, y1], fill=SIDEBAR_BG)
    draw.line([(x1, y0), (x1, y1)], fill=BORDER_LIGHT, width=1)

    # Toggle button
    btn_y1 = y0 + 36
    draw.rectangle([x0, y0, x1, btn_y1], fill=(248, 250, 252))
    draw.line([(x0, btn_y1), (x1, btn_y1)], fill=BORDER_LIGHT, width=1)
    draw.text((x0 + (SIDEBAR_W - 10) // 2, y0 + 10), "‹", font=F_UI_MD, fill=TEXT_MUTED)

    # "Style" header
    sh_y0 = btn_y1
    sh_y1 = sh_y0 + 36
    draw.rectangle([x0, sh_y0, x1, sh_y1], fill=SIDEBAR_BG)
    draw.line([(x0, sh_y1), (x1, sh_y1)], fill=BORDER_LIGHT, width=1)
    draw.text((x0 + 16, sh_y0 + 12), "STYLE", font=F_UI_XS, fill=TEXT_MUTED)

    # Section rows
    sections = ["Page", "Typography", "Colors", "Header / Footer"]
    sy = sh_y1
    for sec in sections:
        draw.line([(x0, sy), (x1, sy)], fill=BORDER_LIGHT, width=1)
        draw.text((x0 + 16, sy + 10), sec, font=F_UI_SM, fill=(100, 116, 139))

        # Draw some fake controls
        if sec == "Page":
            # Paper size picker
            cw, ch = SIDEBAR_W - 32, 22
            draw.rounded_rectangle([x0 + 16, sy + 28, x0 + 16 + cw, sy + 28 + ch],
                                   radius=3, fill=(248, 250, 252),
                                   outline=BORDER_LIGHT)
            draw.text((x0 + 24, sy + 33), "A4", font=F_UI_SM, fill=TEXT_DARK)
            sy += 58
        elif sec == "Typography":
            cw, ch = SIDEBAR_W - 32, 22
            draw.rounded_rectangle([x0 + 16, sy + 28, x0 + 16 + cw, sy + 28 + ch],
                                   radius=3, fill=(248, 250, 252),
                                   outline=BORDER_LIGHT)
            draw.text((x0 + 24, sy + 33), "Georgia", font=F_UI_SM, fill=TEXT_DARK)
            # Size slider
            slider_y = sy + 60
            draw.rounded_rectangle([x0 + 16, slider_y, x0 + 16 + cw, slider_y + 4],
                                   radius=2, fill=BORDER_LIGHT)
            draw.ellipse([x0 + 16 + int(cw * 0.45), slider_y - 4,
                          x0 + 16 + int(cw * 0.45) + 12, slider_y + 8],
                         fill=ACCENT_1)
            sy += 80
        elif sec == "Colors":
            # Two colour swatches
            for i, col in enumerate([(99, 102, 241), (30, 41, 59)]):
                cx = x0 + 16 + i * 36
                cy = sy + 28
                draw.rounded_rectangle([cx, cy, cx + 24, cy + 18],
                                       radius=3, fill=col, outline=BORDER_LIGHT)
            sy += 55
        else:
            sy += 48

    # Reset button at bottom
    rb_y = H - 46
    draw.line([(x0, rb_y - 8), (x1, rb_y - 8)], fill=BORDER_LIGHT, width=1)
    draw.rounded_rectangle([x0 + 12, rb_y, x1 - 12, rb_y + 28],
                           radius=4, fill=None, outline=BORDER_LIGHT)
    draw.text((x0 + 30, rb_y + 8), "Reset to defaults", font=F_UI_SM, fill=TEXT_MUTED)


def draw_editor(draw: ImageDraw.ImageDraw, lines: list[str],
                cursor_line: int = -1, cursor_col: int = -1):
    """Render the markdown editor panel."""
    x0 = SIDEBAR_W
    x1 = SIDEBAR_W + EDITOR_W
    y0 = EDITOR_TOP
    draw.rectangle([x0, y0, x1, H], fill=EDITOR_BG)
    draw.line([(x1, y0), (x1, H)], fill=(40, 50, 70), width=1)

    # Line numbers background strip
    LN_W = 32
    draw.rectangle([x0, y0, x0 + LN_W, H], fill=(10, 16, 28))

    px = x0 + LN_W + 12
    py = y0 + 16
    line_h = 20

    for i, line in enumerate(lines):
        if py + line_h > H - 4:
            break
        ln = i + 1

        # Line number
        draw.text((x0 + 4, py + 2), str(ln), font=F_MONO_SM, fill=(55, 65, 81))

        # Cursor highlight
        if i == cursor_line:
            draw.rectangle([x0 + LN_W, py - 1, x1, py + line_h - 1],
                           fill=(20, 30, 52))

        # Syntax colour
        _draw_editor_line(draw, line, px, py)

        # Cursor caret
        if i == cursor_line and cursor_col >= 0:
            col_text = line[:cursor_col]
            cx = px + F_MONO.getbbox(col_text + " ")[2] - 4
            draw.line([(cx, py), (cx, py + line_h - 2)],
                      fill=(129, 140, 248), width=2)

        py += line_h

    # Scrollbar
    sb_x = x1 - 6
    draw.rectangle([sb_x, y0, x1, H], fill=(13, 20, 36))
    sb_h = 60
    draw.rounded_rectangle([sb_x + 1, y0 + 20, x1 - 1, y0 + 20 + sb_h],
                           radius=2, fill=(40, 50, 70))


def _draw_editor_line(draw: ImageDraw.ImageDraw, line: str, px: int, py: int):
    """Render one editor line with basic syntax highlighting."""
    if not line:
        return

    max_x = SIDEBAR_W + EDITOR_W - 50   # right margin

    # Heading line
    if line.startswith("# ") or line.startswith("## ") or line.startswith("### "):
        parts = line.split(" ", 1)
        hashes = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        draw.text((px, py), hashes, font=F_MONO, fill=SYN_HASH)
        hx = px + F_MONO.getbbox(hashes + " ")[2]
        draw.text((hx, py), rest, font=F_MONO, fill=SYN_HEADING)
        return

    # Table row
    if "|" in line:
        col = SYN_TABLE_PIPE if line.strip().startswith("|") else SYN_PLAIN
        # Alternate pipe/content colour
        out_x = px
        for ch in line:
            if out_x > max_x:
                break
            c = SYN_TABLE_PIPE if ch == "|" else SYN_PLAIN
            draw.text((out_x, py), ch, font=F_MONO, fill=c)
            out_x += F_MONO.getbbox(ch)[2]
        return

    # Separator row (----)
    if set(line.strip()) <= set("-|: "):
        draw.text((px, py), line[:60], font=F_MONO, fill=(70, 80, 100))
        return

    # Bold markers
    if "**" in line:
        parts = line.split("**")
        ox = px
        for j, part in enumerate(parts):
            if ox > max_x:
                break
            clr = SYN_BOLD_MARK if j % 2 == 1 else SYN_PLAIN
            marker = "**" if j < len(parts) - 1 else ""
            draw.text((ox, py), part, font=F_MONO, fill=clr)
            ox += F_MONO.getbbox(part + " ")[2]
        return

    # List item
    if line.startswith("- ") or line.startswith("* "):
        draw.text((px, py), "•", font=F_MONO, fill=ACCENT_1)
        draw.text((px + 14, py), line[2:], font=F_MONO, fill=SYN_PLAIN)
        return

    # Block-quote
    if line.startswith("> "):
        draw.line([(px, py + 2), (px, py + 16)], fill=ACCENT_2, width=2)
        draw.text((px + 8, py), line[2:], font=F_MONO, fill=(100, 116, 139))
        return

    # Code fence
    if line.startswith("```"):
        draw.text((px, py), line, font=F_MONO, fill=(70, 80, 100))
        return

    # Default plain
    draw.text((px, py), line, font=F_MONO, fill=SYN_PLAIN)


def draw_preview(draw: ImageDraw.ImageDraw, preview_state: str):
    """Render the preview panel."""
    x0 = SIDEBAR_W + EDITOR_W
    x1 = W
    y0 = EDITOR_TOP
    draw.rectangle([x0, y0, x1, H], fill=PREVIEW_BG)

    px = x0 + 28
    py = y0 + 20
    max_w = PREVIEW_W - 56

    def h1(text: str):
        nonlocal py
        draw.text((px, py), text, font=F_PREV_H1, fill=PREV_H1)
        py += 32
        # underline
        draw.line([(px, py - 6), (px + max_w, py - 6)], fill=BORDER_LIGHT, width=1)
        py += 4

    def h2(text: str):
        nonlocal py
        draw.text((px, py), text, font=F_PREV_H2, fill=PREV_H2)
        py += 26

    def body(text: str):
        nonlocal py
        # Simple word-wrap
        words = text.split()
        line_words: list[str] = []
        for w in words:
            test = " ".join(line_words + [w])
            bb = F_PREV_BODY.getbbox(test)
            if bb[2] - bb[0] > max_w and line_words:
                draw.text((px, py), " ".join(line_words),
                          font=F_PREV_BODY, fill=PREV_BODY)
                py += 18
                line_words = [w]
            else:
                line_words.append(w)
        if line_words:
            draw.text((px, py), " ".join(line_words),
                      font=F_PREV_BODY, fill=PREV_BODY)
            py += 18

    def bullet(text: str):
        nonlocal py
        draw.ellipse([px, py + 5, px + 5, py + 10], fill=PREV_BODY)
        draw.text((px + 14, py), text, font=F_PREV_BODY, fill=PREV_BODY)
        py += 18

    def spacer(n: int = 8):
        nonlocal py
        py += n

    def table(headers: list[str], rows: list[list[str]]):
        nonlocal py
        col_w = max_w // len(headers)
        row_h = 22
        # Header
        draw.rectangle([px, py, px + max_w, py + row_h],
                       fill=(99, 102, 241))
        for ci, h in enumerate(headers):
            draw.text((px + ci * col_w + 8, py + 5), h,
                      font=F_PREV_SM, fill=(255, 255, 255))
        py += row_h
        for ri, row in enumerate(rows):
            bg = PREV_TABLE_EVEN if ri % 2 == 0 else PREVIEW_BG
            draw.rectangle([px, py, px + max_w, py + row_h], fill=bg)
            draw.line([(px, py), (px + max_w, py)], fill=BORDER_LIGHT, width=1)
            for ci, cell in enumerate(row):
                draw.text((px + ci * col_w + 8, py + 5), cell,
                          font=F_PREV_SM, fill=PREV_BODY)
            py += row_h
        draw.rectangle([px, py - row_h * len(rows) - row_h,
                        px + max_w, py],
                       fill=None, outline=BORDER_LIGHT)
        py += 8

    if preview_state == "idle":
        h1("Welcome to mdPDF")
        spacer(4)
        body("Start writing Markdown on the left — your formatted preview appears here instantly.")
        spacer(12)
        h2("What's supported")
        spacer(4)
        for item in ["Bold, italic, strikethrough, inline code",
                     "Tables, task lists, blockquotes",
                     "Syntax-highlighted code blocks"]:
            bullet(item)
        spacer(12)
        h2("A sample table")
        spacer(6)
        table(["Feature", "Status"],
              [["Live preview", "✅ Done"],
               ["PDF export", "✅ Done"],
               ["File upload", "✅ Done"],
               ["Style sidebar", "✅ Done"]])

    elif preview_state == "heading_added":
        h1("My Report")
        spacer(8)
        body("Start writing Markdown on the left — your formatted preview appears here instantly.")
        spacer(12)
        h2("What's supported")
        spacer(4)
        for item in ["Bold, italic, strikethrough, inline code",
                     "Tables, task lists, blockquotes",
                     "Syntax-highlighted code blocks"]:
            bullet(item)

    elif preview_state == "table_added":
        h1("My Report")
        spacer(8)
        body("Start writing Markdown on the left — your formatted preview appears here instantly.")
        spacer(12)
        h2("Project Status")
        spacer(6)
        table(["Task", "Owner", "Status"],
              [["Design", "Alice", "Done"],
               ["Backend", "Bob", "In progress"],
               ["Testing", "Carol", "Pending"],
               ["Deploy", "Dave", "Pending"]])

    elif preview_state == "saved":
        h1("My Report")
        spacer(8)
        body("Start writing Markdown on the left — your formatted preview appears here instantly.")
        spacer(12)
        h2("Project Status")
        spacer(6)
        table(["Task", "Owner", "Status"],
              [["Design", "Alice", "Done"],
               ["Backend", "Bob", "In progress"],
               ["Testing", "Carol", "Pending"],
               ["Deploy", "Dave", "Pending"]])
        # Saved toast
        toast_w, toast_h = 130, 32
        tx = x0 + (PREVIEW_W - toast_w) // 2
        ty = H - 60
        draw.rounded_rectangle([tx, ty, tx + toast_w, ty + toast_h],
                               radius=6, fill=(34, 197, 94))
        draw.text((tx + 20, ty + 9), "✓  Saved!", font=F_BTN, fill=(255, 255, 255))


def draw_save_dialog(draw: ImageDraw.ImageDraw, img: Image.Image):
    """OS-style save dialog overlay."""
    # Dim background
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 140))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
    draw = ImageDraw.Draw(img)

    # Dialog box
    dw, dh = 420, 240
    dx = (W - dw) // 2
    dy = (H - dh) // 2
    draw.rounded_rectangle([dx, dy, dx + dw, dy + dh], radius=10,
                           fill=(248, 250, 252), outline=(203, 213, 225), width=1)

    # Title bar
    draw.rounded_rectangle([dx, dy, dx + dw, dy + 44], radius=10, fill=(241, 245, 249))
    draw.rectangle([dx, dy + 30, dx + dw, dy + 44], fill=(241, 245, 249))
    draw.text((dx + 18, dy + 13), "Save PDF", font=F_UI_LG, fill=TEXT_DARK)
    # Close button
    draw.ellipse([dx + dw - 30, dy + 13, dx + dw - 15, dy + 28], fill=(252, 165, 165))
    draw.line([(dx + dw - 25, dy + 18), (dx + dw - 20, dy + 23)], fill=(220, 80, 80), width=1)
    draw.line([(dx + dw - 20, dy + 18), (dx + dw - 25, dy + 23)], fill=(220, 80, 80), width=1)

    # File name field
    fnx0, fny0 = dx + 18, dy + 64
    draw.text((fnx0, fny0), "File name:", font=F_UI_SM, fill=TEXT_MUTED)
    draw.rounded_rectangle([fnx0, fny0 + 18, fnx0 + dw - 36, fny0 + 42],
                           radius=4, fill=PREVIEW_BG, outline=(196, 206, 220))
    draw.text((fnx0 + 10, fny0 + 26), "my-report.pdf", font=F_UI_MD, fill=TEXT_DARK)
    # cursor blink in field
    cx_field = fnx0 + 10 + F_UI_MD.getbbox("my-report.pdf")[2] + 2
    draw.line([(cx_field, fny0 + 26), (cx_field, fny0 + 40)], fill=ACCENT_1, width=2)

    # Location row
    lox = fnx0
    loy = fny0 + 56
    draw.text((lox, loy), "Save in:", font=F_UI_SM, fill=TEXT_MUTED)
    draw.rounded_rectangle([lox, loy + 18, lox + dw - 36, loy + 40],
                           radius=4, fill=(241, 245, 249), outline=(196, 206, 220))
    draw.text((lox + 10, loy + 25), "C:\\Users\\ibrah\\Documents", font=F_UI_SM, fill=TEXT_MUTED)

    # Buttons
    cancel_x = dx + dw - 190
    save_x   = dx + dw - 90
    by       = dy + dh - 46
    # Cancel
    draw.rounded_rectangle([cancel_x, by, cancel_x + 80, by + 28],
                           radius=4, fill=PREVIEW_BG, outline=(196, 206, 220))
    draw.text((cancel_x + 20, by + 9), "Cancel", font=F_BTN, fill=TEXT_DARK)
    # Save
    draw_h_gradient(img, save_x, by, save_x + 80, by + 28, ACCENT_1, ACCENT_2)
    draw.rounded_rectangle([save_x, by, save_x + 80, by + 28],
                           radius=4, fill=None, outline=(80, 90, 180))
    draw.text((save_x + 22, by + 9), "Save", font=F_BTN, fill=(255, 255, 255))


# ── Markdown editor content states ────────────────────────────────────────────
LINES_IDLE = [
    "# Welcome to mdPDF",
    "",
    "Start writing **Markdown** on the left —",
    "your formatted preview appears here.",
    "",
    "## What's supported",
    "",
    "- **Bold**, *italic*, ~~strikethrough~~",
    "- Tables, task lists, blockquotes",
    "- Syntax-highlighted code blocks",
    "",
    "## A sample table",
    "",
    "| Feature       | Status  |",
    "|---------------|---------|",
    "| Live preview  | ✅ Done  |",
    "| PDF export    | ✅ Done  |",
]

LINES_HEADING = [
    "# My Report",
    "",
    "Start writing **Markdown** on the left —",
    "your formatted preview appears here.",
    "",
    "## What's supported",
    "",
    "- **Bold**, *italic*, ~~strikethrough~~",
    "- Tables, task lists, blockquotes",
    "- Syntax-highlighted code blocks",
]

LINES_TABLE = [
    "# My Report",
    "",
    "Start writing **Markdown** on the left —",
    "",
    "## Project Status",
    "",
    "| Task    | Owner | Status      |",
    "|---------|-------|-------------|",
    "| Design  | Alice | Done        |",
    "| Backend | Bob   | In progress |",
    "| Testing | Carol | Pending     |",
    "| Deploy  | Dave  | Pending     |",
]


# ── Frame builder ─────────────────────────────────────────────────────────────
def make_frame(editor_lines: list[str],
               preview_state: str = "idle",
               export_state: str = "idle",
               show_dialog: bool = False,
               cursor_line: int = -1,
               cursor_col: int = -1) -> Image.Image:
    img = Image.new("RGB", (W, H), APP_BG)
    draw = ImageDraw.Draw(img)

    draw_top_strip(draw, img)
    draw_header(draw, img, export_state=export_state)
    draw_panel_labels(draw)
    draw_sidebar(draw)
    draw_format_toolbar(draw)
    draw_editor(draw, editor_lines, cursor_line=cursor_line, cursor_col=cursor_col)
    draw_preview(draw, preview_state)

    if show_dialog:
        draw_save_dialog(draw, img)

    return img


# ── Scene list ────────────────────────────────────────────────────────────────
scenes = [
    # 1. App open, idle
    dict(ms=1500, state=dict(editor_lines=LINES_IDLE, preview_state="idle")),

    # 2. User types "# My Report" — typing animation (3 partial frames)
    dict(ms=150, state=dict(editor_lines=["# "] + LINES_IDLE[1:],
                            preview_state="idle", cursor_line=0, cursor_col=2)),
    dict(ms=150, state=dict(editor_lines=["# My "] + LINES_IDLE[1:],
                            preview_state="idle", cursor_line=0, cursor_col=5)),
    dict(ms=300, state=dict(editor_lines=LINES_HEADING,
                            preview_state="idle", cursor_line=0, cursor_col=10)),

    # 3. Preview updates with heading
    dict(ms=800, state=dict(editor_lines=LINES_HEADING,
                            preview_state="heading_added", cursor_line=0, cursor_col=10)),

    # 4. User adds table (typing partial)
    dict(ms=200, state=dict(editor_lines=LINES_HEADING + ["", "## Project Status", ""],
                            preview_state="heading_added", cursor_line=12, cursor_col=0)),
    dict(ms=200, state=dict(editor_lines=LINES_HEADING + ["", "## Project Status", "",
                                                           "| Task    | Owner |"],
                            preview_state="heading_added", cursor_line=13, cursor_col=18)),
    dict(ms=200, state=dict(editor_lines=LINES_HEADING + ["", "## Project Status", "",
                                                           "| Task    | Owner | Status |",
                                                           "|---------|-------|--------|"],
                            preview_state="heading_added", cursor_line=14, cursor_col=24)),

    # 5. Preview shows table
    dict(ms=900, state=dict(editor_lines=LINES_TABLE,
                            preview_state="table_added")),

    # 6. Export PDF clicked — generating spinner
    dict(ms=500, state=dict(editor_lines=LINES_TABLE,
                            preview_state="table_added",
                            export_state="generating")),

    # 7. Save dialog
    dict(ms=1200, state=dict(editor_lines=LINES_TABLE,
                             preview_state="table_added",
                             export_state="generating",
                             show_dialog=True)),

    # 8. Success — saved toast
    dict(ms=1500, state=dict(editor_lines=LINES_TABLE,
                             preview_state="saved",
                             export_state="idle")),

    # 9. Back to idle
    dict(ms=800, state=dict(editor_lines=LINES_TABLE,
                            preview_state="table_added",
                            export_state="idle")),
]


# ── Render + save ─────────────────────────────────────────────────────────────
OUTPUT_PATH = r"C:\Users\ibrah\cascadeProjects\winmdpdf\demo.gif"
SIZE_BUDGET_MB = 2.0

print(f"Rendering {len(scenes)} frames at {W}×{H}…")
frames = []
for i, scene in enumerate(scenes):
    state = scene["state"]
    f = make_frame(
        editor_lines=state.get("editor_lines", LINES_IDLE),
        preview_state=state.get("preview_state", "idle"),
        export_state=state.get("export_state", "idle"),
        show_dialog=state.get("show_dialog", False),
        cursor_line=state.get("cursor_line", -1),
        cursor_col=state.get("cursor_col", -1),
    )
    frames.append(f)
    print(f"  frame {i+1}/{len(scenes)}")

print("Quantizing to 128 colors…")
durations = [s["ms"] for s in scenes]

def save_gif(frames, colors: int, path: str):
    quant = [f.quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                        dither=Image.Dither.NONE) for f in frames]
    quant[0].save(
        path,
        save_all=True,
        append_images=quant[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    return os.path.getsize(path)

size = save_gif(frames, 128, OUTPUT_PATH)
size_mb = size / 1_000_000
print(f"Saved ({size_mb:.2f} MB) → {OUTPUT_PATH}")

if size_mb > SIZE_BUDGET_MB:
    print(f"Over budget ({size_mb:.2f} MB > {SIZE_BUDGET_MB} MB). Retrying with 64 colors…")
    size = save_gif(frames, 64, OUTPUT_PATH)
    size_mb = size / 1_000_000
    print(f"Resaved ({size_mb:.2f} MB) → {OUTPUT_PATH}")

print("Done.")
