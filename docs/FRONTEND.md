## Frontend (Vite + React) — Inclusive Credit UI

### Overview
This is a privacy-first, demo-friendly UI that sits in front of the FastAPI scoring service. It favors:
- **PII-light defaults:** hashed/allowlisted audit payloads, no raw identifiers rendered.
- **Explainability:** reason codes surfaced immediately after scoring.
- **Fairness:** synthetic batch fairness explorer that can call the API endpoint when configured.
- **Audit transparency:** redacted audit table that mirrors backend allowlisting.

### Tech stack
- Vite + React + TypeScript
- React Query for data fetching
- React Hook Form for input management
- Lightweight CSS (glassmorphism, gradients) with no external UI kit

### Running locally
```bash
cd frontend
npm install
npm run dev
```
The dev server runs on `http://localhost:5173`.

### Pointing to the API
The UI auto-falls back to mock data unless `VITE_API_BASE_URL` is set.
```bash
echo 'VITE_API_BASE_URL=http://localhost:8000' > frontend/.env.local
```
- Keep backend API key enforcement disabled (dev) or set headers via a simple proxy if needed.
- Audit data is already redacted on the backend; the UI also avoids rendering raw features.

### Privacy guardrails in the UI
- Applicant IDs are treated as opaque tokens and displayed only in hashed/redacted form from the API.
- Feature payloads are not echoed back to the screen; only derived scores, reason codes, and fairness aggregates are shown.
- The fairness panel uses categorical synthetic groups; replace with aggregated production outcomes that exclude direct identifiers.

### What’s on the screen
- **Hero + metrics:** quick read on decision and fairness deltas.
- **Scoring form:** sliders for alternative-data features, optional audit context (kept categorical).
- **Fairness monitor:** generates synthetic outcome rows or calls `/v1/audit/fairness`.
- **Audit table:** renders allowlisted payloads from `/v1/audit/events`; safe by construction.

### Production hardening notes
- Serve via CDN or container; use HTTPS and an API gateway that injects API keys/headers server-side.
- Consider enabling CSP, subresource integrity, and strict transport security when deploying.
- Keep environment configuration out of the bundle; supply `VITE_API_BASE_URL` at build time per environment.

