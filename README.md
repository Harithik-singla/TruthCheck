# TruthCheck

AI-powered misinformation detector. Paste a news URL → get a credibility score, extracted claims, and fact-check evidence.

## Stack
- **Backend:** FastAPI + Celery + PostgreSQL + Redis
- **ML:** BERT (fine-tuned) + FAISS + spaCy + sentence-transformers
- **Frontend:** React + TypeScript + Vite
- **DevOps:** Docker Compose + GitHub Actions

## Quick start

```bash
# 1. Clone repo
git clone https://github.com/yourusername/truthcheck
cd truthcheck

# 2. Copy env file and fill in values
cp .env.example .env

# 3. Start all services
docker compose up --build

# 4. API docs at:
#    http://localhost:8000/docs
```

## Local development (without Docker)

```bash
cd backend
poetry install
cp ../.env.example ../.env

# Start just DB and Redis via Docker
docker compose up db redis -d

# Run the API
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest
```

## Project structure

```
truthcheck/
├── backend/           # FastAPI app
│   ├── app/
│   │   ├── api/       # route handlers
│   │   ├── core/      # config, logging, celery
│   │   ├── models/    # pydantic schemas
│   │   └── services/  # business logic
│   └── tests/
├── ml/                # training scripts & notebooks
├── frontend/          # React app (Week 4)
└── extension/         # Chrome extension (Week 4)
```
