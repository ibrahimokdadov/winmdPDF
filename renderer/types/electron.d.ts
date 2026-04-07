import type { StyleSettings } from '../lib/style-settings'

export {}

export interface RecentFile {
  name: string
  path: string
  openedAt: number
}

declare global {
  interface Window {
    electronAPI: {
      exportPDF(
        markdown: string,
        settings: StyleSettings
      ): Promise<{ success: boolean; error?: string }>
      openFile(): Promise<{ name: string; path: string; content: string } | null>
      readFile(filePath: string): Promise<{ name: string; path: string; content: string }>
      getRecentFiles(): Promise<RecentFile[]>
      addRecentFile(entry: RecentFile): Promise<RecentFile[]>
    }
  }
}
