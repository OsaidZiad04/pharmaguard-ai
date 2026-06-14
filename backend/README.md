# Backend

FastAPI backend for PharmaGuard AI.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
pytest
```

## Endpoints

- `GET /health`
- `POST /prescriptions/analyze-text`
- `GET /drugs/{drug_name}`
- `POST /counseling/generate`

All current logic is placeholder/mock logic. Do not use outputs for final medical decisions.
