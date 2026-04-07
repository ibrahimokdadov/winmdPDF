import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  exportPDF: (markdown: string, settings: unknown) =>
    ipcRenderer.invoke('export-pdf', markdown, settings),
  openFile: () =>
    ipcRenderer.invoke('open-file'),
  readFile: (filePath: string) =>
    ipcRenderer.invoke('read-file', filePath),
  getRecentFiles: () =>
    ipcRenderer.invoke('get-recent-files'),
  addRecentFile: (entry: { name: string; path: string; openedAt: number }) =>
    ipcRenderer.invoke('add-recent-file', entry),
})
