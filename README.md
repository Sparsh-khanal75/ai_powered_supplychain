This starter includes a FastAPI app with SQLAlchemy async models and an Inventory router implemented.

## Setup
1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and update `DATABASE_URL`.

3. Run Postgres (locally or Docker). Example Docker command:

```bash
docker run --name mcp-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=mcp_db -p 5432:5432 -d postgres:15
```

4. Start the app:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Open Swagger UI at `http://localhost:8000/docs`