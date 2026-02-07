# Signal > Noise

Behavioral intelligence pipeline that ingests events and feedback, clusters users into cohorts, detects anomalies, and serves explainable insights.

```mermaid
flowchart LR
  UI[React Frontend] --> API[FastAPI API]
  API --> DB[(Postgres/Supabase)]
  API --> ML[ML Pipeline]
  ML --> DB
```

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Demo Data
```bash
python data/generate_synthetic.py
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/signal_noise \
  python backend/scripts/seed_db.py
```

## API Examples

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"demo","password":"demo"}'
```

```bash
curl -X POST http://localhost:8000/api/events \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <TOKEN>' \
  -d '{"user_id":1,"event_type":"signup","metadata":{"source":"ad"},"timestamp":"2026-02-07T12:00:00Z"}'
```

```bash
curl -X GET 'http://localhost:8000/api/insights?limit=10' \
  -H 'Authorization: Bearer <TOKEN>'
```

## Data Samples

Users CSV:
```
id,created_at,plan,country
1,2026-01-10T12:00:00Z,free,US
2,2026-01-12T10:30:00Z,pro,GB
```

Events CSV:
```
user_id,event_type,metadata,timestamp
1,feature_use,{'feature': 'export'},2026-01-15T12:00:00Z
2,login,{},2026-01-16T09:00:00Z
```

Feedback CSV:
```
user_id,text,rating,timestamp
1,Love it,5,2026-01-20T08:30:00Z
2,Confusing UI,2,2026-01-20T09:10:00Z
```

## Deploy

### Docker Compose
```bash
docker compose up --build
```

### Notes
- Configure `DATABASE_URL` and `JWT_SECRET_KEY` in `.env`.
- `OPENAI_API_KEY` is optional and can be used to swap in a real LLM in the explanation module.

