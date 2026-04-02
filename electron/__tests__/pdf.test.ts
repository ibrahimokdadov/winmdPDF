import { buildHeaderFooterTemplate, getPrintToPdfOptions } from '../pdf'
import { DEFAULT_SETTINGS } from '../../renderer/lib/style-settings'

describe('buildHeaderFooterTemplate', () => {
  it('returns empty span for empty text', () => {
    expect(buildHeaderFooterTemplate('', false)).toBe('<span></span>')
  })

  it('replaces {page} with pageNumber span', () => {
    const result = buildHeaderFooterTemplate('{page}', false)
    expect(result).toContain('<span class="pageNumber"></span>')
  })

  it('replaces {total} with totalPages span', () => {
    const result = buildHeaderFooterTemplate('{total}', false)
    expect(result).toContain('<span class="totalPages"></span>')
  })

  it('replaces {date} with ISO date', () => {
    const result = buildHeaderFooterTemplate('{date}', false)
    expect(result).toMatch(/\d{4}-\d{2}-\d{2}/)
  })

  it('includes border-top when showLine is true', () => {
    expect(buildHeaderFooterTemplate('Header', true)).toContain('border-top')
  })

  it('does not include border when showLine is false', () => {
    expect(buildHeaderFooterTemplate('Footer', false)).not.toContain('border-top')
  })
})

describe('getPrintToPdfOptions', () => {
  it('maps A4 portrait to pageSize A4, landscape false', () => {
    const opts = getPrintToPdfOptions({ ...DEFAULT_SETTINGS, pageFormat: 'A4', pageOrientation: 'portrait' })
    expect(opts.pageSize).toBe('A4')
    expect(opts.landscape).toBe(false)
  })

  it('maps landscape orientation correctly', () => {
    const opts = getPrintToPdfOptions({ ...DEFAULT_SETTINGS, pageOrientation: 'landscape' })
    expect(opts.landscape).toBe(true)
  })

  it('maps Presentation to custom micron dimensions', () => {
    const opts = getPrintToPdfOptions({ ...DEFAULT_SETTINGS, pageFormat: 'Presentation' })
    expect(opts.pageSize).toEqual({ width: 254000, height: 143000 })
    expect(opts.landscape).toBe(false)
  })

  it('converts margins from mm to inches', () => {
    const opts = getPrintToPdfOptions({ ...DEFAULT_SETTINGS, marginTop: 25.4, marginBottom: 12.7 })
    expect(opts.margins?.top).toBeCloseTo(1.0)
    expect(opts.margins?.bottom).toBeCloseTo(0.5)
  })

  it('sets marginType to custom', () => {
    const opts = getPrintToPdfOptions(DEFAULT_SETTINGS)
    expect(opts.margins?.marginType).toBe('custom')
  })
})
