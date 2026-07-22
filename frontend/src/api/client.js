const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Core request helper. Attaches the bearer token when provided,
 * parses JSON, and throws a readable Error on non-2xx responses
 * so callers can just try/catch and show err.message.
 */
async function request(path, { method = 'GET', body, token } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  let data = null
  try {
    data = await res.json()
  } catch {
    // no JSON body (e.g. some error responses) — that's fine
  }

  if (!res.ok) {
    const detail = data?.detail || `Request failed (${res.status})`
    throw new Error(detail)
  }

  return data
}

export function signup({ username, email, password }) {
  return request('/signup', {
    method: 'POST',
    body: { username, email, password },
  })
}

export function login({ email, password }) {
  return request('/login', {
    method: 'POST',
    body: { email, password },
  })
}

export function saveInterests(token, interests) {
  return request('/user/interests', {
    method: 'POST',
    body: { interests },
    token,
  })
}

export function fetchNews(token) {
  return request('/fetch-news', {
    method: 'POST',
    token,
  })
}

export function getSummary(token) {
  return request('/summary', {
    method: 'GET',
    token,
  })
}

export { API_BASE }
