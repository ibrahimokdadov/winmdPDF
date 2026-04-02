import Image from 'next/image'

const GITHUB   = 'https://github.com/ibrahimokdadov/winmdPDF'
const RELEASES = 'https://github.com/ibrahimokdadov/winmdPDF/releases'
const WEB_APP  = 'https://mdpdf.whhite.com'

const FEATURES = [
  { label: 'Live preview',       desc: 'See formatted output as you type.' },
  { label: 'Mermaid diagrams',   desc: 'Flowcharts, sequence diagrams, Gantt, ER — rendered in preview and PDF.' },
  { label: 'Style sidebar',      desc: 'Fonts, margins, line height, header/footer text. Saved between sessions.' },
  { label: 'Format toolbar',     desc: 'Bold, italic, color, highlight, font size — applied to selected text.' },
  { label: 'No Puppeteer',       desc: "PDF rendering uses Electron's built-in Chromium. No second download." },
  { label: 'No Docker, no server', desc: 'Open the app and go. Works fully offline.' },
]

const GH_ICON = (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
  </svg>
)

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">

      {/* Top accent strip */}
      <div className="h-[3px]" style={{ background: 'linear-gradient(90deg, #6366f1, #8b5cf6, #d946ef)' }} />

      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-4 border-b border-slate-800/60">
        <div className="flex items-center gap-1.5 select-none">
          <span className="font-serif italic text-white text-xl" style={{ fontWeight: 400, letterSpacing: '-0.02em' }}>md</span>
          <svg className="w-4 h-4 text-indigo-400 mx-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
          <span className="font-serif text-white text-xl" style={{ fontWeight: 400, letterSpacing: '-0.02em' }}>PDF</span>
          <span className="ml-2 text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-indigo-400 border border-slate-700">desktop</span>
        </div>
        <div className="flex items-center gap-5">
          <a href={WEB_APP} target="_blank" rel="noopener noreferrer"
             className="text-sm text-slate-500 hover:text-slate-200 transition-colors">
            web version
          </a>
          <a href={GITHUB} target="_blank" rel="noopener noreferrer"
             className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-200 transition-colors">
            {GH_ICON} GitHub
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex flex-col items-center text-center px-6 pt-20 pb-14">
        <h1 className="text-5xl font-bold mb-4 text-slate-100" style={{ letterSpacing: '-0.03em' }}>
          Write Markdown.<br />Get a PDF.
        </h1>
        <p className="text-lg max-w-xl mb-8 text-slate-400 leading-relaxed">
          Desktop app for Windows, macOS, and Linux. Live preview, Mermaid diagrams,
          custom fonts and margins. No Docker, no server, no Puppeteer.
        </p>
        <div className="flex items-center gap-3 flex-wrap justify-center">
          <a href={RELEASES} target="_blank" rel="noopener noreferrer"
             className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold text-white hover:opacity-90 transition-opacity"
             style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', boxShadow: '0 1px 2px rgba(99,102,241,0.4)' }}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </a>
          <a href={GITHUB} target="_blank" rel="noopener noreferrer"
             className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold text-slate-200 bg-slate-800 border border-slate-700 hover:border-indigo-400 transition-colors">
            {GH_ICON} View source
          </a>
          <a href={WEB_APP} target="_blank" rel="noopener noreferrer"
             className="text-sm text-slate-500 hover:text-indigo-400 transition-colors">
            or try the web version →
          </a>
        </div>
      </section>

      {/* Demo GIF */}
      <section className="flex justify-center px-6 pb-16">
        <div className="rounded-xl overflow-hidden w-full max-w-3xl border border-slate-800"
             style={{ boxShadow: '0 0 60px rgba(99,102,241,0.1)' }}>
          <Image
            src="/demo.gif"
            alt="mdPDF desktop app demo"
            width={900}
            height={580}
            unoptimized
            className="w-full"
          />
        </div>
      </section>

      {/* Features */}
      <section className="max-w-4xl mx-auto px-6 pb-20">
        <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))' }}>
          {FEATURES.map(f => (
            <div key={f.label} className="rounded-lg p-5 bg-slate-900 border border-slate-800">
              <div className="text-sm font-semibold mb-1.5 text-indigo-400">{f.label}</div>
              <div className="text-sm leading-relaxed text-slate-500">{f.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center pb-10 text-xs text-slate-700">
        <a href={GITHUB} target="_blank" rel="noopener noreferrer" className="text-slate-600 hover:underline">
          github.com/ibrahimokdadov/winmdPDF
        </a>
        {' · '}
        <a href={WEB_APP} target="_blank" rel="noopener noreferrer" className="text-slate-600 hover:underline">
          mdpdf.whhite.com
        </a>
      </footer>

    </div>
  )
}
