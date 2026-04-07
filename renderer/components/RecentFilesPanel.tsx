'use client'

import { useState } from 'react'
import type { RecentFile } from '@/types/electron'

interface Props {
  files: RecentFile[]
  onOpen: (file: { name: string; path: string; content: string }) => void
  onFilesChange: (files: RecentFile[]) => void
}

function timeAgo(ts: number): string {
  const diff = Date.now() - ts
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const d = Math.floor(h / 24)
  return `${d}d ago`
}

export default function RecentFilesPanel({ files, onOpen, onFilesChange }: Props) {
  const [collapsed, setCollapsed] = useState(false)
  const [loading, setLoading] = useState<string | null>(null)

  async function handleOpen(file: RecentFile) {
    if (!window.electronAPI) return
    setLoading(file.path)
    try {
      const result = await window.electronAPI.readFile(file.path)
      const updated = await window.electronAPI.addRecentFile({ name: result.name, path: result.path, openedAt: Date.now() })
      onFilesChange(updated)
      onOpen(result)
    } catch {
      // file may have moved — remove it from recents
      const filtered = files.filter(f => f.path !== file.path)
      onFilesChange(filtered)
    } finally {
      setLoading(null)
    }
  }

  if (files.length === 0) return null

  return (
    <div
      style={{
        background: 'rgba(10, 14, 28, 0.95)',
        borderBottom: '1px solid rgba(99,102,241,0.15)',
        flexShrink: 0,
        overflow: 'hidden',
      }}
    >
      {/* Header row */}
      <button
        onClick={() => setCollapsed(c => !c)}
        className="flex items-center gap-2 w-full px-5 text-left group"
        style={{ height: '28px' }}
      >
        <svg
          className="text-indigo-500 flex-shrink-0 transition-transform duration-200"
          style={{ width: '10px', height: '10px', transform: collapsed ? 'rotate(-90deg)' : 'rotate(0deg)' }}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
        <span className="text-[10px] font-medium uppercase tracking-[0.15em] text-slate-500 group-hover:text-slate-400 transition-colors">
          Recent
        </span>
        <span className="text-[10px] text-slate-600 ml-0.5">
          {files.length}
        </span>
      </button>

      {/* File chips */}
      {!collapsed && (
        <div
          className="flex items-center gap-1.5 px-5 overflow-x-auto pb-2"
          style={{ scrollbarWidth: 'none' }}
        >
          {files.map(file => (
            <button
              key={file.path}
              onClick={() => handleOpen(file)}
              disabled={loading === file.path}
              title={file.path}
              className="flex items-center gap-1.5 flex-shrink-0 rounded-md transition-all duration-150"
              style={{
                padding: '4px 8px',
                background: loading === file.path ? 'rgba(99,102,241,0.15)' : 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.07)',
                maxWidth: '180px',
              }}
              onMouseEnter={e => {
                if (loading !== file.path) {
                  (e.currentTarget as HTMLButtonElement).style.background = 'rgba(99,102,241,0.12)'
                  ;(e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(99,102,241,0.3)'
                }
              }}
              onMouseLeave={e => {
                if (loading !== file.path) {
                  (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255,255,255,0.04)'
                  ;(e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255,255,255,0.07)'
                }
              }}
            >
              {/* File icon */}
              <svg className="w-3 h-3 text-indigo-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span
                className="text-[11px] text-slate-300 truncate"
                style={{ maxWidth: '120px' }}
              >
                {file.name}
              </span>
              <span className="text-[9px] text-slate-600 flex-shrink-0 ml-0.5">
                {timeAgo(file.openedAt)}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
