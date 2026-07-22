import { useState } from 'react'
import { fetchNews, getSummary } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { parseSummary } from '../utils/parseSummary.js'

export default function SummaryPanel() {
  const { token } = useAuth()

  const [fetching, setFetching] = useState(false)
  const [summarizing, setSummarizing] = useState(false)
  const [chunksStored, setChunksStored] = useState(null)
  const [sections, setSections] = useState([])
  const [error, setError] = useState('')

  async function handleFetchNews() {
    setError('')
    setFetching(true)
    try {
      const data = await fetchNews(token)
      setChunksStored(data.chunks_stored ?? 0)
    } catch (err) {
      setError(err.message)
    } finally {
      setFetching(false)
    }
  }

  async function handleGetSummary() {
    setError('')
    setSummarizing(true)
    try {
      const data = await getSummary(token)
      setSections(parseSummary(data.summary))
    } catch (err) {
      setError(err.message)
    } finally {
      setSummarizing(false)
    }
  }

  return (
    <section className="summary-panel">
      <h2>News</h2>

      {error && <p className="form-error">{error}</p>}

      <div className="summary-actions">
        <button type="button" onClick={handleFetchNews} disabled={fetching}>
          {fetching ? 'Refreshing…' : 'Refresh news'}
        </button>
        <button type="button" onClick={handleGetSummary} disabled={summarizing}>
          {summarizing ? 'Summarizing…' : 'Get summary'}
        </button>
        {chunksStored !== null && (
          <span className="chunk-readout">{chunksStored} chunks stored</span>
        )}
      </div>

      <div className="summary-sections">
        {sections.length === 0 && (
          <p className="empty-state">
            No summary yet. Set your interests, refresh the news, then request a summary.
          </p>
        )}

        {sections.map((section, idx) => (
          <article className="summary-card" key={`${section.topic}-${idx}`}>
            <h3>{section.topic}</h3>
            {section.bullets.length > 0 && (
              <ul>
                {section.bullets.map((bullet, i) => (
                  <li key={i}>{bullet}</li>
                ))}
              </ul>
            )}
            {section.paragraphs.map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </article>
        ))}
      </div>
    </section>
  )
}
