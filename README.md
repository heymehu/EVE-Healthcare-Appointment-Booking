# EVE Healthcare

Diagnostic test booking platform built for the EVE Healthcare SDE Intern Backend Engineering assignment.

Users can sign up, browse diagnostic centres, book tests, complete a **simulated** payment, and track booking status. The backend is the primary focus: JWT auth, PostgreSQL, booking/payment state transitions, and **idempotent payment webhooks**.

## Features

- User signup/login with bcrypt password hashing and JWT access tokens
- Browse/search diagnostic centres and tests from the database
- Create bookings (`PENDING`)
- Simulated payments (`SUCCESS` / `FAILED` / `AUTO` 80/20)
- Webhook processing with `provider_event_id` uniqueness (idempotent)
- Users can only access/cancel their own bookings
- Swagger docs at `/docs`
- React frontend matching the reference UI
- Docker Compose for PostgreSQL + API + frontend + Redis + Celery
- Pytest coverage for the required flows
- **Rate limiting** (IP-based, configurable via `slowapi`)
- **Redis caching** for centres list, categories, cities, and individual centres
- **Celery background jobs** for webhook retry, notifications, and cleanup tasks

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic, PyJWT, bcrypt |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Background Jobs | Celery 5 (Redis broker/result backend) |
| Rate Limiting | slowapi |
| Frontend | React, Vite, React Router |
| Tests | pytest, FastAPI TestClient |
| Packaging | Docker, Docker Compose |

## Architecture

```
frontend (React)
    ↓ HTTP + JWT
backend/app
    routers     → HTTP adapters
    services    → booking/payment/webhook/auth business rules
    models      → SQLAlchemy tables
    schemas     → request/response validation
    core        → config, security, database session, redis, rate limiting
PostgreSQL ←→ Redis (cache + Celery broker)
    ↑
Celery Worker (webhook retry, notifications, cleanup)
Celery Beat (periodic tasks)
```

Routers do not contain business logic. Services own state transitions.

## Database schema

**users** — `id`, `name`, `email` (unique), `password_hash`, `created_at`

**diagnostic_centres** — `id`, `name`, `location`, `description`, `image_url`, `rating`, `review_count`, `centre_type`, `address`, `city`, `pincode`, `phone`, `accreditation`, `panels`, `open_time`, `is_open_now`, `starting_price`, `created_at`

**tests** — `id`, `centre_id` (FK), `name`, `description`, `category`, `price`, `created_at`

**bookings** — `id`, `user_id` (FK), `test_id` (FK), `centre_id` (FK), `appointment_date`, `appointment_time`, `amount`, `status`, `created_at`, `updated_at`

**payments** — `id`, `booking_id` (FK), `status`, `provider_event_id` (**UNIQUE**), `created_at`, `updated_at`

`description`, `image_url`, `rating`, `review_count`, `centre_type`, `address`, `city`, `pincode`, `phone`, `accreditation`, `panels`, `open_time`, `is_open_now`, `starting_price`, and `category` are UI/display fields on top of the required assignment columns.

## Authentication flow

1. `POST /auth/signup` hashes the password with bcrypt and stores `password_hash` only.
2. `POST /auth/login` verifies the hash and returns a JWT (`sub` = user id).
3. Protected routes use `Authorization: Bearer <token>`.
4. A user can only read, pay for, or cancel bookings they own (`403` otherwise).

## Booking / payment state transitions

```
Create booking          → booking.status = PENDING
POST /payments SUCCESS  → payment.status = SUCCESS, booking.status = CONFIRMED
POST /payments FAILED   → payment.status = FAILED,   booking.status = FAILED
Retry after FAILED      → new payment row, booking moves to CONFIRMED or FAILED
PATCH cancel            → PENDING or CONFIRMED → CANCELLED
Webhook SUCCESS/FAILED  → same mapping, unless booking is already CANCELLED
```

`POST /payments/` is a mock processor. No Razorpay/Stripe/PayPal. Optional `simulate_status`: `SUCCESS`, `FAILED`, or `AUTO` (≈80% success).

## Webhook idempotency

`POST /payments/webhook/`

```json
{
  "event_id": "evt_12345",
  "payment_id": 10,
  "booking_id": 20,
  "status": "SUCCESS"
}
```

- `payments.provider_event_id` has a **UNIQUE** constraint.
- The first event with a given `event_id` is applied.
- The same `event_id` again returns `200` with `{ "idempotent": true, "processed": false }` and does **not** create another payment/booking or rewrite state.
- Concurrent duplicates are caught via `IntegrityError` and treated as idempotent.
- Unknown payment/booking → `404`. Invalid payload/status → `422`/`400`.
- If `WEBHOOK_SECRET` is set, the `X-Webhook-Secret` header must match.
- **Webhook retry**: Transient failures (5xx) are queued to Celery for automatic retry (max 3 attempts, 60s backoff).

## Rate Limiting

- IP-based rate limiting via `slowapi` with Redis storage (falls back to in-memory).
- Default: 100 requests per 60 seconds per IP.
- Configurable via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS`.
- Returns `429 Too Many Requests` with `Retry-After` header when exceeded.

## Caching

- Redis caching for centre listings, categories, cities, and individual centres.
- Cache keys include query parameters for list endpoints.
- TTL configurable via `CACHE_TTL_SECONDS` (default 300s).
- Gracefully falls back to in-memory dict when Redis unavailable (e.g., during tests).

## API endpoints

| Method | Path | Auth |
| --- | --- | --- |
| POST | `/auth/signup` | No |
| POST | `/auth/login` | No |
| GET | `/centres/` | No |
| GET | `/centres/{centre_id}` | No |
| GET | `/centres/{centre_id}/tests` | No |
| GET | `/tests/{test_id}` | No |
| POST | `/bookings/` | Yes |
| GET | `/bookings/` | Yes |
| GET | `/bookings/{booking_id}` | Yes |
| PATCH | `/bookings/{booking_id}/cancel` | Yes |
| POST | `/payments/` | Yes |
| POST | `/payments/webhook/` | Secret header if configured |
| GET | `/health` | No |
| GET | `/docs` `/openapi.json` | No |

## Environment variables

Copy `.env.example` to `backend/.env`:

```
DATABASE_URL=postgresql+psycopg2://eve:eve@localhost:5432/eve_healthcare
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
WEBHOOK_SECRET=
ENVIRONMENT=development

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=10

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Caching
CACHE_ENABLED=true
CACHE_TTL_SECONDS=300
```

Do not commit real secrets. JWT and database credentials are not hardcoded in application code.

## Local setup

### 1. PostgreSQL

```bash
docker compose up db -d
```

### 2. Redis (for caching, rate limiting, Celery)

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 3. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # or cp .env.example .env
python seed.py
uvicorn app.main:app --reload --port 8000
```

Swagger: http://localhost:8000/docs

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173 (Vite proxies API calls to port 8000)

### 5. Celery Worker (optional, for background jobs)

```bash
cd backend
.venv\Scripts\activate
celery -A app.celery_app worker --loglevel=info --concurrency=4
```

### 6. Celery Beat (optional, for periodic tasks)

```bash
cd backend
.venv\Scripts\activate
celery -A app.celery_app beat --loglevel=info
```

## Docker

```bash
docker compose up --build
```

- API: http://localhost:8000
- Frontend: http://localhost:3000
- Postgres: localhost:5432
- Redis: localhost:6379
- Celery Worker: background (logs in compose output)
- Celery Beat: background (schedules periodic tasks)

Set `SECRET_KEY` in a root `.env` before using Compose in anything other than local demo.

## Tests

```bash
cd backend
pytest -q
```

Tests use an isolated in-memory SQLite database and cover signup, login, centres, tests, bookings, authorization, payments, webhooks (including duplicates), and cancellation. Redis/Celery features gracefully fall back to in-memory implementations during tests.

## Sample requests

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Mehul Kumar\",\"email\":\"mehul@example.com\",\"password\":\"secret123\"}"

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"mehul@example.com\",\"password\":\"secret123\"}"

curl http://localhost:8000/centres/

curl -X POST http://localhost:8000/bookings/ \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"test_id\":1,\"centre_id\":1,\"appointment_date\":\"2026-10-03\",\"appointment_time\":\"10:00:00\"}"

curl -X POST http://localhost:8000/payments/ \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"booking_id\":1,\"simulate_status\":\"SUCCESS\"}"

curl -X POST http://localhost:8000/payments/webhook/ \
  -H "Content-Type: application/json" \
  -d "{\"event_id\":\"evt_12345\",\"payment_id\":1,\"booking_id\":1,\"status\":\"SUCCESS\"}"
```

Sample login response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": { "id": 1, "name": "Mehul Kumar", "email": "mehul@example.com", "created_at": "..." }
}
```

## Assumptions

- Appointment slots are accepted between 07:00 and 20:00; dates cannot be in the past.
- A FAILED booking can be retried with another `POST /payments/` (new payment row).
- CONFIRMED bookings cannot be paid again; they can be cancelled before the appointment date.
- Webhooks may update an existing payment; they never insert a second booking.
- Display codes such as `#BK0001` are formatted from the integer primary key.
- Extra centre fields (rating, image, address, etc.) exist only to match the reference UI.
- Rate limiting and caching gracefully degrade to in-memory when Redis is unavailable.

## Future improvements

- Signed webhook payloads (HMAC) in addition to a shared secret
- Alembic migrations instead of `create_all`
- Refresh tokens and httpOnly cookie storage
- Slot inventory / double-booking prevention at the time-window level
- WebSocket support for real-time booking status updates
- Admin dashboard for centre/test management