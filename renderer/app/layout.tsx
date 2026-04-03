import type { Metadata } from 'next'
import { Fraunces, Plus_Jakarta_Sans, Fira_Code } from 'next/font/google'
import './globals.css'
import 'github-markdown-css/github-markdown-light.css'

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-fraunces',
  display: 'swap',
  axes: ['opsz'],
})

const jakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-jakarta',
  display: 'swap',
  weight: ['400', '500', '600'],
})

const firaCode = Fira_Code({
  subsets: ['latin'],
  variable: '--font-fira',
  display: 'swap',
  weight: ['400', '500'],
})

const SITE_URL = 'https://winmdpdf.whhite.com'
const TITLE = 'mdPDF — Markdown to PDF'
const DESCRIPTION = 'Write Markdown, export to PDF. Live preview, Mermaid diagrams, custom fonts and margins. Desktop app for Windows, macOS, and Linux. No Docker required.'

export const metadata: Metadata = {
  title: TITLE,
  description: DESCRIPTION,
  metadataBase: new URL(SITE_URL),
  alternates: { canonical: '/' },
  robots: { index: true, follow: true },
  icons: { icon: '/favicon.svg' },
  openGraph: {
    type: 'website',
    url: SITE_URL + '/',
    title: TITLE,
    description: DESCRIPTION,
    images: [{ url: '/og-image.svg', width: 1200, height: 630, alt: 'mdPDF — Markdown to PDF' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: TITLE,
    description: DESCRIPTION,
    images: ['/og-image.svg'],
  },
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'mdPDF',
  description: DESCRIPTION,
  url: SITE_URL,
  applicationCategory: 'UtilitiesApplication',
  operatingSystem: 'Windows, macOS, Linux',
  offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
  author: { '@type': 'Person', email: 'ibrahim@whhite.com' },
  softwareVersion: '1.0.0',
  downloadUrl: 'https://github.com/ibrahimokdadov/winmdPDF/releases',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${fraunces.variable} ${jakarta.variable} ${firaCode.variable}`}>
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>{children}</body>
    </html>
  )
}
