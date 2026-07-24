# Cake Marketplace -- Backend

FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL, with Alembic migrations.
Domain-per-bakery multi-tenant SaaS model -- see below.

## Run it

**Docker (recommended)**
```
cp .env.example .env   # set at least JWT_SECRET
docker compose up --build
python seed.py          # creates a demo bakery + owner to test against
```
API at `http://localhost:8000` (interactive docs at `/docs`). Postgres at
`localhost:5432` (`cake`/`cake`/`cake_marketplace`). The container's
entrypoint waits for Postgres, runs `alembic upgrade head`, then starts
`uvicorn` with `--reload` against the bind-mounted code.

If rebuilding after a previous failed run: `docker compose down -v` first
to clear any partial state.

**Local venv**
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # fill in DATABASE_URL against your own Postgres
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

## Structure

```
app/
  core/          config, database session, JWT auth + RBAC
  models/        one file per domain entity (SQLAlchemy)
  schemas/       one file per domain entity (Pydantic), mirrors models/
  services/      tenant resolution, order pricing
  routers/       one file per resource -- the only layer that touches HTTP
  main.py
migrations/      Alembic environment + versioned migrations
deploy/          production reverse-proxy config (Caddy, on-demand TLS)
seed.py          local-dev demo tenant
```

Each package's `__init__.py` re-exports its contents, so the rest of the
app does `from app.models import User, Bakery` etc. without needing to
know which file a class lives in.

## Multi-tenancy: one domain per bakery
This is a SaaS model, not a shared marketplace -- each bakery gets its
own domain (a platform subdomain like `sweetfig.cakeplatform.test`, or
later a verified custom domain), and a customer on that domain only ever
sees that one bakery's catalog. `app/services/tenant.py` is the single
place that resolves an incoming hostname to the `Bakery` row that owns
it; both the public resolve endpoint and auth enforcement build on it.

**Accounts are tenant-scoped, not global**: `username` is unique per
bakery, not platform-wide -- the same username can exist at two
different bakeries. Registration and login both require an
`X-Tenant-Host` header identifying which bakery's storefront the request
is for. That header must only ever be set by the frontend's own server
(reading the real, browser-supplied Host header) -- never trust it if
this backend were ever exposed directly to the public internet.

**Registration is intentionally lightweight**: just `username` +
`password`. Name, phone, and email are optional, added later via
`PATCH /users/me`.

## API reference

| Endpoint | Notes |
|---|---|
| `POST /auth/register` | username + password, tenant-scoped via `X-Tenant-Host` |
| `POST /auth/login` | OAuth2 password form, same tenant scoping |
| `GET /users/me` | current user profile |
| `PATCH /users/me` | update name/phone/email |
| `GET /bakeries` | list verified bakeries |
| `GET /bakeries/resolve?host=` | public, unauthenticated: hostname -> bakery |
| `GET /bakeries/me` | the bakery owned by the current user |
| `PATCH /bakeries/me` | update name/location/mpesa_till |
| `GET /bakeries/{id}` | fetch by id |
| `GET /templates?bakery_id=` | list a bakery's designs |
| `POST /templates` | create a design (bakery_owner/admin, scoped to their own bakery) |
| `GET /templates/{id}` | fetch by id |
| `POST /blueprints` | save a customized cake design |
| `GET /blueprints/{id}` | fetch by id |
| `GET /orders` | role-aware list: customer -> their orders, bakery_owner -> their bakery's orders, admin -> all |
| `POST /orders` | place an order from a blueprint (price is calculated, see below) |
| `GET /orders/{id}` | fetch by id (customer who placed it, or the owning bakery/admin) |
| `PATCH /orders/{id}/status` | bakery_owner/admin only |
| `GET /internal/domain-check` | for the reverse proxy only, never public -- see `deploy/README.md` |

## Order pricing
`app/services/pricing.py` -- template's base price plus a flat KSh 200
surcharge per sticker layer. This is a deliberately simple placeholder,
not a rules engine; swap in per-bakery pricing rules or per-asset
pricing once that's needed. It replaces the old `price = 0.0` stub.

## Migrations
Schema changes go through Alembic, not ad hoc scripts:
- `alembic revision --autogenerate -m "describe the change"` after editing a model
- `alembic upgrade head` to apply

Note on `0001_initial.py`: its enum columns use `create_type=False`
because `op.create_table` will otherwise also try to create the same
Postgres enum type as a side effect of the column, and collide with the
explicit `.create()` call -- keep that pattern for any future migration
that adds an enum column.

## Known gaps (by design, not oversight)
- **Bakery self-service signup** doesn't exist -- the only way a new
  tenant comes into being right now is `seed.py`. Building this properly
  means solving "how do you register before your tenant exists" (a
  platform-level flow, distinct from the tenant-scoped `/auth/register`
  above) plus domain verification -- worth its own pass.
- **M-Pesa STK push** isn't wired up -- `POST /orders` calculates a real
  price but doesn't take payment yet. Needs real Daraja sandbox
  credentials to build against.
- **Sticker/asset catalog** has no admin management endpoints yet, and
  pricing doesn't yet vary per sticker -- see the pricing note above.

## Production reverse proxy
`deploy/Caddyfile` + `deploy/README.md` cover on-demand TLS -- the piece
that makes arbitrary bakery-owned domains work in production without
manually issuing a certificate per domain. Not wired into
`docker-compose.yml` yet since the frontend isn't containerized; see
that doc for how it plugs in once it is.

See `../docs/cake-marketplace-system-design.md` for the full architecture and ADRs.
