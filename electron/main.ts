import { app, BrowserWindow, ipcMain, protocol, net, dialog } from 'electron'
import { join } from 'path'
import { pathToFileURL } from 'url'
import { readFile, writeFile, mkdir } from 'fs/promises'
import { exportToPdf } from './pdf'
import type { StyleSettings } from '../renderer/lib/style-settings'

interface RecentFile {
  name: string
  path: string
  openedAt: number
}

const MAX_RECENT = 10

async function getRecentFilesPath() {
  return join(app.getPath('userData'), 'recent-files.json')
}

async function loadRecentFiles(): Promise<RecentFile[]> {
  try {
    const filePath = await getRecentFilesPath()
    const raw = await readFile(filePath, 'utf-8')
    return JSON.parse(raw)
  } catch {
    return []
  }
}

async function saveRecentFiles(files: RecentFile[]) {
  const filePath = await getRecentFilesPath()
  await mkdir(join(app.getPath('userData')), { recursive: true })
  await writeFile(filePath, JSON.stringify(files, null, 2), 'utf-8')
}

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

ipcMain.handle('open-file', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [{ name: 'Markdown', extensions: ['md', 'markdown', 'txt'] }],
  })
  if (result.canceled || result.filePaths.length === 0) return null
  const filePath = result.filePaths[0]
  const content = await readFile(filePath, 'utf-8')
  const name = filePath.split(/[\\/]/).pop() ?? filePath
  return { name, path: filePath, content }
})

ipcMain.handle('read-file', async (_event, filePath: string) => {
  const content = await readFile(filePath, 'utf-8')
  const name = filePath.split(/[\\/]/).pop() ?? filePath
  return { name, path: filePath, content }
})

ipcMain.handle('get-recent-files', async () => {
  return loadRecentFiles()
})

ipcMain.handle('add-recent-file', async (_event, entry: RecentFile) => {
  const files = await loadRecentFiles()
  const filtered = files.filter(f => f.path !== entry.path)
  const updated = [{ ...entry, openedAt: Date.now() }, ...filtered].slice(0, MAX_RECENT)
  await saveRecentFiles(updated)
  return updated
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
