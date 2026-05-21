# Student Management API

REST API for managing students and academic groups, built with **FastAPI**, **SQLAlchemy** (async), and **PostgreSQL**.

---

## Tech stack

| Layer        | Library                          |
|--------------|----------------------------------|
| Framework    | FastAPI                          |
| ORM          | SQLAlchemy 2.x (async)           |
| DB driver    | asyncpg                          |
| Database     | PostgreSQL 15                    |
| Validation   | Pydantic v2 + pydantic-settings  |
| Server       | Uvicorn                          |
| Container    | Docker + Docker Compose          |

---

## Project structure

```
StudentAPI/
├── routers/
│   ├── __init__.py       # Package marker
│   ├── students.py       # Student endpoints
│   └── groups.py         # Group endpoints
├── main.py               # App factory & lifespan
├── config.py             # Settings (loaded from .env)
├── database.py           # Engine, session factory, DatabaseManager
├── models.py             # SQLAlchemy ORM models
├── schemas.py            # Pydantic request / response schemas
├── crud.py               # Database operations (no HTTP logic)
├── requirements.txt      # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── .env                  # Environment variables (not committed)
```

---

## Getting started

### 1. Clone and configure

```bash
git clone <repo-url>
cd StudentAPI
cp .env.example .env   # fill in your values
```

`.env` example:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/student_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=student_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

| Service  | URL                        |
|----------|----------------------------|
| API      | http://localhost:8000      |
| Swagger  | http://localhost:8000/docs |
| Adminer  | http://localhost:8080      |

### 3. Run locally (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Make sure PostgreSQL is running and .env is configured
uvicorn main:app --reload
```

---

## API endpoints

### Students `/api/v1/students`

| Method | Path                                        | Description                    |
|--------|---------------------------------------------|--------------------------------|
| POST   | `/`                                         | Create a student               |
| GET    | `/`                                         | List all students              |
| GET    | `/{student_id}`                             | Get a student by ID            |
| DELETE | `/{student_id}`                             | Delete a student               |
| POST   | `/{student_id}/group/{group_id}`            | Assign student to a group      |
| DELETE | `/{student_id}/group/`                      | Remove student from their group|
| PUT    | `/{student_id}/transfer/{new_group_id}`     | Transfer student to new group  |

### Groups `/api/v1/groups`

| Method | Path                        | Description               |
|--------|-----------------------------|---------------------------|
| POST   | `/`                         | Create a group            |
| GET    | `/`                         | List all groups           |
| GET    | `/{group_id}`               | Get a group by ID         |
| DELETE | `/{group_id}`               | Delete a group            |
| GET    | `/{group_id}/students`      | List students in a group  |

Full interactive documentation is available at **http://localhost:8000/docs** (Swagger UI).

---

## Design notes

- **Denormalised `members_count`** — the `Group` model stores a running counter of its members. This avoids a `COUNT(*)` query every time a group is fetched. The counter is kept consistent by the CRUD helpers `_increment_members_count` / `_decrement_members_count`.
- **Layered architecture** — HTTP concerns (status codes, `HTTPException`) live exclusively in the routers; the CRUD layer returns plain ORM objects or booleans and knows nothing about HTTP.
- **Async throughout** — all database I/O uses `AsyncSession` so the event loop is never blocked.