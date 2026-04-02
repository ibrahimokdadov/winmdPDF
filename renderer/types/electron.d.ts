import type { StyleSettings } from '../lib/style-settings'

export {}

declare global {
  interface Window {
    electronAPI: {
      exportPDF(
        markdown: string,
        settings: StyleSettings
      ): Promise<{ success: boolean; error?: string }>
    }
  }
}
