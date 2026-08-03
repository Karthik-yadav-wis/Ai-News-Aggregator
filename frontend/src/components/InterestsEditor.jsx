import { useState } from 'react'
import { saveInterests } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

export default function InterestsEditor({ interests, setInterests }) {
  const { token } = useAuth()
  const [draft, setDraft] = useState('')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  function addInterest() {
    const value = draft.trim()
    if (!value) return
    const exists = interests.some((i) => i.toLowerCase() === value.toLowerCase())
    if (!exists) setInterests([...interests, value])
    setDraft('')
  }

  function removeInterest(idx) {
    setInterests(interests.filter((_, i) => i !== idx))
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') {
      e.preventDefault()
      addInterest()
    }
  }

  async function handleSave() {
    setError('')
    setMessage('')

    if (!interests.length) {
      setError('Add at least one interest first.')
      return
    }

    setSaving(true)
    try {
      await saveInterests(token, interests)
      setMessage('Interests saved.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="interests-editor">
      <h2>Your interests</h2>

      {error && <p className="form-error">{error}</p>}
      {message && <p className="form-success">{message}</p>}

      <div className="interest-input-row">
        <input
          type="text"
          placeholder="Add a topic — e.g. chess"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button type="button" onClick={addInterest}>
          Add
        </button>
      </div>

      <ul className="interest-tags">
        {interests.map((name, idx) => (
          <li key={name} className="interest-tag">
            {name}
            <button
              type="button"
              aria-label={`Remove ${name}`}
              onClick={() => removeInterest(idx)}
            >
              ×
            </button>
          </li>
        ))}
      </ul>

      <button type="button" onClick={handleSave} disabled={saving}>
        {saving ? 'Saving…' : 'Save interests'}
      </button>
    </section>
  )
}
