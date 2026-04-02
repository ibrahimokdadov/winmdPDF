import { app, BrowserWindow, ipcMain, protocol, net } from 'electron'
import { join } from 'path'
import { pathToFileURL } from 'url'
import { exportToPdf } from './pdf'
import type { StyleSettings } from '../renderer/lib/style-settings'

const isDev = !app.isPackaged

// Register custom protocol for serving static Next.js files in production
// This fixes absolute paths like /_next/static/... that break under file://
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { standard: true, secure: true, supportFetchAPI: true } },
])

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'mdPDF',
    webPreferences: {
      preload: join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  if (isDev) {
    win.loadURL('http://localhost:3000')
  } else {
    win.loadURL('app://index.html')
  }
}

ipcMain.handle('export-pdf', async (_event, markdown: string, settings: StyleSettings) => {
  return exportToPdf(markdown, settings)
})

app.whenReady().then(() => {
  // Register app:// protocol to serve renderer/out/ static files
  protocol.handle('app', (request) => {
    try {
      const { pathname } = new URL(request.url)
      const relPath = pathname.replace(/^\//, '')
      const outDir = join(app.getAppPath(), 'renderer/out')
      const filePath = join(outDir, relPath || 'index.html')
      // Guard against path traversal
      const resolvedOut = outDir.replace(/\\/g, '/')
      const resolvedFile = filePath.replace(/\\/g, '/')
      if (!resolvedFile.startsWith(resolvedOut + '/') && resolvedFile !== resolvedOut) {
        return new Response('Forbidden', { status: 403 })
      }
      return net.fetch(pathToFileURL(filePath).toString())
    } catch {
      return new Response('Not Found', { status: 404 })
    }
  })

  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
