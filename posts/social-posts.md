# Social posts — winmdPDF

---

## LinkedIn

### Technical

winmdPDF is an Electron desktop app that wraps the mdpdf web app and runs it offline, on Windows, macOS, and Linux.

The PDF export is the part worth understanding. The web version uses Puppeteer, which means your machine downloads a second copy of Chromium specifically to render PDFs. Electron already ships with Chromium. So we deleted the Puppeteer pipeline and replaced it with `webContents.printToPDF()` -> the same engine, called directly.

Export flows through IPC. When you click Export, the renderer calls `window.electronAPI.exportPDF(markdown, settings)` through a contextBridge. The main process opens a hidden BrowserWindow, loads the rendered HTML, polls every 100ms until Mermaid SVGs are done (or 5 seconds pass), then calls printToPDF with the margin and page size from your style settings. The OS save dialog handles the rest.

The renderer is a static Next.js export, served via a custom `app://` protocol handler. File:// URLs break with Next.js absolute asset paths, so the handler resolves requests relative to `renderer/out/` with a path traversal guard.

One Chromium. No server. No Docker. The app is under 150MB.

---

### ELI5

Think of a word processor, but you write in plain text with small symbols: asterisks for bold, hashtags for headers. That's Markdown.

winmdPDF is an editor for that. You type on the left, see a formatted preview on the right, click Export, get a PDF. The diagrams work too - if you write out a flowchart or sequence diagram in code, it renders visually in the preview and comes out correctly in the PDF.

No website. No account. Just an app.

---

### Why we built it

Self-hosting mdpdf requires Docker. There's Puppeteer inside, which pulls in its own Chromium, so the image is heavy and setup takes more than a few minutes if you just want to convert a Markdown file.

I used the web version at mdpdf.whhite.com often enough that I wanted it local. No server, no Docker, no Chromium process sitting in the background waiting for requests.

The Electron path made sense once I realized we were already using Chromium for rendering. The app was downloading it twice. Once we cut Puppeteer and plugged into Electron's `webContents` directly, the whole thing simplified.

The Electron approach cut the Docker requirement entirely.

---

### What makes it different

Most Markdown-to-PDF tools are CLI utilities or web apps. Desktop apps with live preview are uncommon.

winmdPDF has a live preview, a style sidebar (fonts, margins, header/footer text), and Mermaid diagram support. The diagram part is what took work: the main process polls for SVG elements before calling printToPDF, so if your document has a sequence diagram or a flowchart, it shows up in the PDF looking exactly like the preview. I haven't found another desktop Markdown editor where that works reliably, though I'm probably biased.

The other specific thing: no Puppeteer. PDF rendering runs on the Chromium already inside Electron, so there's no second download and no separate process to manage.

---

### Story

A few months back I was writing a design doc. Markdown, as usual. At the end I wanted to send it as a PDF.

I went to mdpdf.whhite.com, pasted the content, adjusted the font and margins, exported. Worked fine. Then did the same thing three more times that week, re-entering the same settings each time because the web app doesn't save them between sessions.

What I wanted was that app, but local. Something that ran offline, remembered the style settings, and let me export without loading a browser tab.

winmdPDF does that. The settings persist. The Mermaid diagrams in those docs came out correctly in the PDF, which took more iteration to get right than I expected.

---

## Twitter / X

### Technical

Built winmdPDF: Electron wrapper for mdpdf. Swapped Puppeteer for Electron's `webContents.printToPDF()` - same Chromium, no second download. PDF via IPC, custom `app://` protocol, under 150MB. #OpenSource

---

### ELI5

Write Markdown on the left, see a preview on the right, click Export, get a PDF. No browser tab, no account, no server. Diagrams work too. That's winmdPDF.

---

### Why we built it

Wanted mdpdf offline. The web version needs Docker and downloads Chromium twice. Electron already has Chromium. Cut Puppeteer, used that.

---

### What makes it different

Desktop Markdown editor where Mermaid diagrams actually render in the PDF output. One Chromium, no Puppeteer.

---

### Story

I kept re-entering the same font and margin settings every time I exported a doc from the web version. Wanted it local, wanted it to remember. Built it.
