import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  exportPDF: (markdown: string, settings: unknown) =>
    ipcRenderer.invoke('export-pdf', markdown, settings),
})
