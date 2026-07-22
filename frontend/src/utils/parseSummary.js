/**
 * The backend's summarizer returns text formatted like:
 *
 *   ## Topic Name
 *   - Key point 1
 *   - Key point 2
 *
 * This turns that into an array of { topic, bullets, paragraphs }
 * so components can render structured cards instead of raw text.
 */
export function parseSummary(summaryText) {
  if (!summaryText || !summaryText.trim()) return []

  const sections = summaryText.split(/\n(?=##\s)/).filter((s) => s.trim())

  if (!sections.length) {
    return [{ topic: 'Summary', bullets: [], paragraphs: [summaryText.trim()] }]
  }

  return sections.map((section) => {
    const lines = section.trim().split('\n').filter((l) => l.trim())
    let topic = 'Summary'
    const bullets = []
    const paragraphs = []

    lines.forEach((line) => {
      const trimmed = line.trim()
      if (trimmed.startsWith('##')) {
        topic = trimmed.replace(/^##+\s*/, '').trim()
      } else if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
        bullets.push(trimmed.replace(/^[-*]\s*/, ''))
      } else {
        paragraphs.push(trimmed)
      }
    })

    return { topic, bullets, paragraphs }
  })
}
