"""
Generate branded GIF cards for winmdPDF social posts.
Colors from renderer/app/globals.css.
Output: posts/gifs/  (10 GIFs, LinkedIn 1200x628, Twitter 1200x675)
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ── Palette (from globals.css) ────────────────────────────────────────────────
BG      = (15,  23,  42)   # #0f172a
TEXT    = (226, 232, 240)  # #e2e8f0
ACCENT  = (129, 140, 248)  # #818cf8
MUTED   = (100, 116, 139)  # #64748b
BORDER  = (51,  65,  85)   # #334155
SURFACE = (30,  41,  59)   # #1e293b

# ── Dimensions ────────────────────────────────────────────────────────────────
LI_W, LI_H = 1200, 628
TW_W, TW_H = 1200, 675

FONT_DIR = "C:/Windows/Fonts/"
OUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "posts", "gifs")

# ── Fonts ─────────────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    candidates = (["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"])
    candidates += ["verdana.ttf"]
    for name in candidates:
        try:
            return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
        except OSError:
            pass
    return ImageFont.load_default()

# Pre-load once
F_BRAND  = load_font(38, bold=True)
F_LABEL  = load_font(22)
F_BODY_L = load_font(27)          # LinkedIn body
F_BODY_T = load_font(33)          # Twitter body  (larger — short text)
F_URL    = load_font(20)

# ── Text wrapping ─────────────────────────────────────────────────────────────
def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], []
    for word in words:
        test = " ".join(current + [word])
        w = draw.textbbox((0, 0), test, font=font)[2]
        if w > max_width and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines

# ── Card chrome ───────────────────────────────────────────────────────────────
def draw_chrome(draw, w, h, label, platform):
    # Background
    draw.rectangle([0, 0, w, h], fill=BG)
    # Left accent bar
    draw.rectangle([0, 0, 7, h], fill=ACCENT)
    # Brand
    draw.text((44, 36), "winmdPDF", font=F_BRAND, fill=ACCENT)
    # Platform badge (top right)
    badge = platform  # "LinkedIn" or "Twitter / X"
    bw = draw.textbbox((0, 0), badge, font=F_LABEL)[2]
    bx = w - bw - 52
    draw.rounded_rectangle([bx - 14, 30, bx + bw + 14, 70], radius=8, fill=SURFACE)
    draw.text((bx, 38), badge, font=F_LABEL, fill=MUTED)
    # Separator
    draw.rectangle([44, 88, w - 44, 90], fill=BORDER)
    # Angle label (bottom left)
    draw.text((44, h - 46), label, font=F_URL, fill=MUTED)
    # URL (bottom right)
    url = "mdpdf.whhite.com"
    uw = draw.textbbox((0, 0), url, font=F_URL)[2]
    draw.text((w - uw - 44, h - 46), url, font=F_URL, fill=MUTED)
    # Bottom separator
    draw.rectangle([44, h - 60, w - 44, h - 58], fill=BORDER)

# ── Frame builders ────────────────────────────────────────────────────────────
def make_linkedin_frame(text, label, show_text):
    img  = Image.new("RGB", (LI_W, LI_H), BG)
    draw = ImageDraw.Draw(img)
    draw_chrome(draw, LI_W, LI_H, label, "LinkedIn")
    if show_text:
        # First paragraph only
        first_para = text.strip().split("\n\n")[0]
        lines = wrap_text(draw, first_para, F_BODY_L, LI_W - 110)
        y, line_h = 112, 44
        for line in lines[:9]:
            draw.text((54, y), line, font=F_BODY_L, fill=TEXT)
            y += line_h
    return img

def make_twitter_frame(text, label, show_text):
    img  = Image.new("RGB", (TW_W, TW_H), BG)
    draw = ImageDraw.Draw(img)
    draw_chrome(draw, TW_W, TW_H, label, "Twitter / X")
    if show_text:
        lines = wrap_text(draw, text.strip(), F_BODY_T, TW_W - 110)
        y, line_h = 118, 54
        for line in lines[:7]:
            draw.text((54, y), line, font=F_BODY_T, fill=TEXT)
            y += line_h
    return img

# ── GIF writer ────────────────────────────────────────────────────────────────
def save_gif(frames, durations, filename):
    path = os.path.join(OUT_DIR, filename)
    for colors in (128, 64):
        q = [f.quantize(colors=colors, dither=0) for f in frames]
        q[0].save(
            path, save_all=True, append_images=q[1:],
            duration=durations, loop=0, optimize=True
        )
        kb = os.path.getsize(path) / 1000
        if kb <= 500:
            break
    print(f"  {filename:<40}  {kb:.0f} KB")

# ── 3-frame animation ─────────────────────────────────────────────────────────
# Frame 1: chrome only       (500 ms  — brand moment)
# Frame 2: chrome + text     (2000 ms — reading time)
# Frame 3: chrome + text     (400 ms  — brief pause before loop)

def gif_li(text, label, slug):
    f = lambda show: make_linkedin_frame(text, label, show)
    save_gif([f(False), f(True), f(True)], [500, 2000, 400], f"linkedin-{slug}.gif")

def gif_tw(text, label, slug):
    f = lambda show: make_twitter_frame(text, label, show)
    save_gif([f(False), f(True), f(True)], [400, 2000, 300], f"twitter-{slug}.gif")

# ── Post content ──────────────────────────────────────────────────────────────

LI_TECHNICAL = """\
winmdPDF is an Electron desktop app that wraps the mdpdf web app and runs it offline, on Windows, macOS, and Linux.

The PDF export is the part worth understanding. The web version uses Puppeteer, which means your machine downloads a second copy of Chromium specifically to render PDFs. Electron already ships with Chromium. So we deleted the Puppeteer pipeline and replaced it with webContents.printToPDF() -- the same engine, called directly."""

LI_ELI5 = """\
Think of a word processor, but you write in plain text with small symbols: asterisks for bold, hashtags for headers. That's Markdown.

winmdPDF is an editor for that. You type on the left, see a formatted preview on the right, click Export, get a PDF. The diagrams work too."""

LI_WHY = """\
Self-hosting mdpdf requires Docker. There's Puppeteer inside, which pulls in its own Chromium, so the image is heavy and setup takes more than a few minutes if you just want to convert a Markdown file.

I used the web version at mdpdf.whhite.com often enough that I wanted it local. No server, no Docker, no Chromium process sitting in the background waiting for requests."""

LI_UNIQUE = """\
Most Markdown-to-PDF tools are CLI utilities or web apps. Desktop apps with live preview are uncommon.

winmdPDF has a live preview, a style sidebar (fonts, margins, header/footer text), and Mermaid diagram support. The main process polls for SVG elements before calling printToPDF, so diagrams show up in the PDF exactly like the preview."""

LI_STORY = """\
A few months back I was writing a design doc. Markdown, as usual. At the end I wanted to send it as a PDF.

I went to mdpdf.whhite.com, pasted the content, adjusted the font and margins, exported. Worked fine. Then did the same thing three more times that week, re-entering the same settings each time."""

TW_TECHNICAL = "Built winmdPDF: Electron wrapper for mdpdf. Swapped Puppeteer for Electron's webContents.printToPDF() - same Chromium, no second download. PDF via IPC, custom app:// protocol, under 150MB. #OpenSource"
TW_ELI5      = "Write Markdown on the left, see a preview on the right, click Export, get a PDF. No browser tab, no account, no server. Diagrams work too. That's winmdPDF."
TW_WHY       = "Wanted mdpdf offline. The web version needs Docker and downloads Chromium twice. Electron already has Chromium. Cut Puppeteer, used that."
TW_UNIQUE    = "Desktop Markdown editor where Mermaid diagrams actually render in the PDF output. One Chromium, no Puppeteer."
TW_STORY     = "I kept re-entering the same font and margin settings every time I exported a doc from the web version. Wanted it local, wanted it to remember. Built it."

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Generating LinkedIn cards...")
    gif_li(LI_TECHNICAL, "Technical",          "technical")
    gif_li(LI_ELI5,      "ELI5",               "eli5")
    gif_li(LI_WHY,       "Why we built it",    "why-built")
    gif_li(LI_UNIQUE,    "What makes it different", "unique")
    gif_li(LI_STORY,     "Story",              "story")

    print("Generating Twitter / X cards...")
    gif_tw(TW_TECHNICAL, "Technical",          "technical")
    gif_tw(TW_ELI5,      "ELI5",               "eli5")
    gif_tw(TW_WHY,       "Why we built it",    "why-built")
    gif_tw(TW_UNIQUE,    "What makes it different", "unique")
    gif_tw(TW_STORY,     "Story",              "story")

    print("Done. Files in posts/gifs/")
