# FastAPI Modular Backend

![CI](https://github.com/vishalsinhacodes/fastapi-modular-backend/actions/workflows/ci.yml/badge.svg)

# FastAPI Modular Backend with PostgreSQL, Redis, JWT Auth, Docker & Alembic

A production-ready backend built using **FastAPI**, implemented with clean architecture principles and modern tooling.  
The system demonstrates real-world features such as authentication, role-based authorization, caching, rate limiting, database migrations, containerization, and fully automated testing.

---

## 🚀 Features

| Capability                                    | Status |
| --------------------------------------------- | ------ |
| User Authentication (JWT-based)               | ✅     |
| Role-Based Authorization (Admin / User)       | ✅     |
| Product CRUD with PostgreSQL + SQLAlchemy ORM | ✅     |
| Alembic Database Migrations                   | ✅     |
| Redis Caching of frequently requested queries | ✅     |
| Rate Limiting per user per route              | ✅     |
| Dockerized Multi-Service Architecture         | ✅     |
| Pytest test suite with 100% working tests     | ✅     |
| Environment-based config (12-Factor)          | ✅     |

---

## 📦 Tech Stack

- **FastAPI**
- **Python 3.11**
- **PostgreSQL**
- **Redis**
- **SQLAlchemy ORM**
- **Alembic**
- **JWT Authentication**
- **Docker & Docker Compose**
- **pytest**
- **Pydantic v2**

---

## 🗂 Folder Structure

```text
app/
 ├── main.py
 ├── core/           → config, logging, redis, security
 ├── models/         → SQLAlchemy ORM models
 ├── schemas/        → Pydantic schemas for validation
 ├── services/       → business logic layer
 ├── routers/        → API endpoints
 ├── dependencies/   → shared dependency functions
 ├── database.py
 └── tests/
```

## 🐳 Running the Project with Docker

docker compose up --build

Once running:

    Swagger UI → http://localhost:8000/docs
    PostgreSQL exposed locally → localhost:5433
    Redis exposed locally → localhost:6379

## 🧰 Running Locally (Without Docker)

1. Create and activate virtual environment:

   python -m venv venv

   # Windows

   .\venv\Scripts\activate

   # Linux / macOS

   source venv/bin/activate

2. Install dependencies:  
   pip install -r requirements.txt

3. Run database migrations:
   alembic upgrade head

4. Start the server:
   uvicorn app.main:app --reload

Swagger UI will be available at: http://localhost:8000/docs

## 🧪 Running Tests

    pytest -q

## 📌 Authentication Flow

1. Register a user → POST /auth/register
2. Login and obtain JWT → POST /auth/login
3. Use the Authorize button in Swagger → paste Bearer <token>
4. Access authenticated routes (e.g. /products)

Admin-only routes (like product deletion) require a user with is_admin = true.

## ⚡ Redis: Caching & Rate Limiting

Redis is used for:

    1. Caching
        -> GET /products responses are cached in Redis for a short TTL.
        -> Cache keys are based on query parameters (skip, limit, filters).
        -> Cache is invalidated when products are created or deleted.

    2. Rate Limiting
        -> Per-user, per-endpoint limits using Redis counters and TTL.
        -> Exceeding the limit returns 429 Too Many Requests.

If Redis is unavailable, the system:
-> Logs a warning at startup.
-> Disables caching and rate limiting gracefully (no API downtime).

## 🧱 Database Schema (High Level)

| Table             | Description                   |
| ----------------- | ----------------------------- |
| `users`           | Stores authentication & roles |
| `products`        | Product catalog & pricing     |
| `alembic_version` | Tracks migration history      |

## 📎 Deployment Notes

This project can be deployed to:
-> Render / Railway / Fly.io
-> AWS ECS / Fargate
-> Azure Container Apps
-> Kubernetes (using the same Docker images)
Because configuration is done via environment variables, it follows 12-Factor principles and is cloud-friendly.

## SequenceDiagram

sequenceDiagram
actor U as User / Client
participant F as FastAPI API
participant R as Redis (Broker + Result)
participant W as Celery Worker

    U->>F: POST /tasks/send-welcome-email
    activate F
    F->>F: Validate user & auth (JWT)
    F->>R: Enqueue task send_welcome_email(email)
    F-->>U: 200 OK ({"task_id": "..."})
    deactivate F

    activate W
    W->>R: Fetch job
    W->>W: Execute send_welcome_email
    W->>R: Store status + result
    deactivate W

    U->>F: GET /tasks/{task_id}
    activate F
    F->>R: Query task state
    F-->>U: {"status": "SUCCESS", "result": "..."}
    deactivate F

## 👤 Author

Vishal Sinha
Backend Engineer | Python Developer
📧 vishalsinha.codes@gmail.com

## If you find this project useful, feel free to ⭐ star the repository!
