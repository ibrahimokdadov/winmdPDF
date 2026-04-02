import { app, BrowserWindow, dialog } from 'electron'
import { writeFile } from 'fs/promises'
import { tmpdir } from 'os'
import { join } from 'path'
import { markdownToHtml } from '../renderer/lib/markdown-to-html'
import type { StyleSettings } from '../renderer/lib/style-settings'

export function buildHeaderFooterTemplate(text: string, showLine: boolean): string {
  if (!text) return '<span></span>'
  const html = text
    .replace('{page}', '<span class="pageNumber"></span>')
    .replace('{total}', '<span class="totalPages"></span>')
    .replace('{date}', new Date().toISOString().slice(0, 10))
  return `<div style="width:100%;font-size:10px;font-family:sans-serif;color:#64748b;padding:0 20mm;${showLine ? 'border-top:1px solid #e2e8f0;' : ''}box-sizing:border-box;">${html}</div>`
}

export function getPrintToPdfOptions(settings: StyleSettings): {
  pageSize: string | { width: number; height: number }
  landscape: boolean
  margins: { marginType: 'custom'; top: number; bottom: number; left: number; right: number }
  printBackground: boolean
  displayHeaderFooter: boolean
  headerTemplate: string
  footerTemplate: string
} {
  const margins = {
    marginType: 'custom' as const,
    top: settings.marginTop / 25.4,
    bottom: settings.marginBottom / 25.4,
    left: settings.marginLeft / 25.4,
    right: settings.marginRight / 25.4,
  }

  const hasHeaderFooter = !!(settings.headerText || settings.footerText)

  const base = {
    margins,
    printBackground: true,
    displayHeaderFooter: hasHeaderFooter,
    headerTemplate: buildHeaderFooterTemplate(settings.headerText, settings.showHeaderLine),
    footerTemplate: buildHeaderFooterTemplate(settings.footerText, settings.showFooterLine),
  }

  if (settings.pageFormat === 'Presentation') {
    return { ...base, pageSize: { width: 254000, height: 143000 }, landscape: false }
  }

  return {
    ...base,
    pageSize: settings.pageFormat,
    landscape: settings.pageOrientation === 'landscape',
  }
}

export async function exportToPdf(markdown: string, settings: StyleSettings): Promise<{ success: boolean; error?: string }> {
  const html = markdownToHtml(markdown, settings, { cssBase: app.getAppPath() })

  const tmpPath = join(tmpdir(), `mdpdf-${Date.now()}.html`)
  await writeFile(tmpPath, html, 'utf-8')

  const win = new BrowserWindow({ show: false, webPreferences: { javascript: true } })

  try {
    await win.loadFile(tmpPath)

    // Wait for all Mermaid diagrams to render (or 5s timeout)
    await win.webContents.executeJavaScript(`
      new Promise((resolve) => {
        const deadline = Date.now() + 5000
        const check = () => {
          const diagrams = Array.from(document.querySelectorAll('.mermaid'))
          const allDone = diagrams.length === 0 || diagrams.every(el => el.querySelector('svg'))
          if (allDone || Date.now() > deadline) resolve(true)
          else setTimeout(check, 100)
        }
        check()
      })
    `)

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const pdfBuffer = await win.webContents.printToPDF(getPrintToPdfOptions(settings) as any)

    const { filePath } = await dialog.showSaveDialog({
      defaultPath: 'output.pdf',
      filters: [{ name: 'PDF', extensions: ['pdf'] }],
    })

    if (!filePath) return { success: false, error: 'Cancelled' }

    await writeFile(filePath, pdfBuffer)
    return { success: true }
  } finally {
    win.close()
    try { require('fs').unlinkSync(tmpPath) } catch { /* ignore */ }
  }
}
