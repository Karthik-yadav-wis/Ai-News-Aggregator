# AI News Assistant — Frontend

Plain React + Vite frontend for the FastAPI/LangChain news backend. Deliberately unstyled beyond a CSS reset — every component uses plain `className` hooks so you can style it however you like.

## Setup

```bash
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if your backend isn't on localhost:8000
npm run dev
```

Runs on http://localhost:5173 by default.

## Before this works against your backend

1. Your FastAPI backend needs CORS middleware enabled for `http://localhost:5173`:
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
2. Backend must be running and reachable at the URL in `.env`.

## Structure

```
src/
  api/client.js           — all backend calls (signup, login, interests, fetch-news, summary)
  context/AuthContext.jsx — JWT token state, persisted in localStorage
  components/
    ProtectedRoute.jsx     — redirects to /login if not authenticated
    InterestsEditor.jsx    — add/remove/save interest tags
    SummaryPanel.jsx        — refresh news + request summary, renders parsed sections
  pages/
    Login.jsx
    Signup.jsx
    Dashboard.jsx           — combines InterestsEditor + SummaryPanel
  utils/parseSummary.js    — parses the backend's "## Topic / - bullet" summary text
```

## Notes

- Routes: `/login`, `/signup`, `/dashboard` (protected — redirects to `/login` if no token).
- The token lives in `localStorage` under the key `ai_news_token`.
- `SummaryPanel` parses the summary text assuming the backend's `## Topic` + `- bullet` format from the prompt template. If you change that prompt's output format, update `src/utils/parseSummary.js` to match.
- No `/chat` page yet — add one when the RAG search/chat endpoint is built on the backend.
