# Logistics Database — DHL-Style Carrier Model

A normalized PostgreSQL relational database modeling express carrier logistics operations (inspired by DHL-style carrier networks), built with SQLAlchemy ORM and managed via Alembic migrations.

## Overview

This project designs and implements a relational (OLTP) database for a logistics/carrier business domain — not a retail e-commerce model. The schema represents how a carrier like DHL manages commercial shipping requests, physical shipment execution, fleet operations, and facility transit, rather than product sales.

12 entities were designed, covering commercial bookings, service tiers, payments, physical shipments and packages, facility/warehouse network nodes, transport routes, fleet assets (vehicles/drivers), and two associative entities resolving many-to-many relationships.

## Project Goals

- Normalized, 3NF-compliant relational schema
- Referential integrity via primary/foreign key constraints
- Real-world logistics business rules reflected in cardinality decisions
- Reproducible local development environment via Docker
- Version-controlled, reversible schema evolution via Alembic migrations

## Tech Stack

- **PostgreSQL 18** — containerized via Docker
- **SQLAlchemy 2.0** (ORM, declarative models)
- **Alembic** — schema migrations
- **Pydantic / pydantic-settings** — configuration and environment variable validation
- **uv** — Python package and environment management
- **DBeaver** — database GUI client
- **pytest** — testing (planned)

## Setup Instructions

### Prerequisites
- Linux (or WSL) with Docker installed
- Python 3.13
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 1. Clone the repository
```bash
git clone https://github.com/Sallie25/logistics_db_project.git
cd logistics_db_project
```

### 2. Set up the Python environment
```bash
uv venv --python 3.13
source .venv/bin/activate
uv sync
```

### 3. Configure environment variables
Copy the example file and fill in your own values:
```bash
cp .env.example .env
```

### 4. Start PostgreSQL via Docker
```bash
docker compose up -d
docker compose ps
```

### 5. Apply database migrations
```bash
alembic upgrade head
```

Verify tables were created by connecting to `logistics_db` in DBeaver (or `psql`) and confirming all 12 tables exist under the `public` schema.

## Environment Variables

Defined in `.env` (never committed — see `.env.example` for the required template):

| Variable | Description |
|---|---|
| `POSTGRES_USER` | Database username |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_HOST` | Database host (`localhost` for local Docker) |
| `POSTGRES_PORT` | Database port (default `5432`) |
| `POSTGRES_DB` | Database name |

## Architecture / Workflow

```
Client (sender/receiver/payer roles)
   │
ShipmentBooking ──1:1── Payment
   │        │
   │        └──N:1── ServiceType
   │ 1:N
   ▼
Shipment ──1:N── Package
   │  (origin/destination → Facility)
   │
   │ 1:N
   ▼
TransportLeg ──N:1── Vehicle
   │         ──N:1── Driver
   │         ──N:1── Route ──N:1── Facility (origin/destination)

Package ──N:M (via PackageFacilityTransit)── Facility
```

**Entity summary (12 entities):**

| Entity | Responsibility |
|---|---|
| Client | People/organizations acting as sender, receiver, or payer |
| ShipmentBooking | Commercial service request from a client |
| ServiceType | Carrier product/service tier (e.g., Express, Standard) |
| Payment | Financial transaction tied to a booking |
| Shipment | One physical movement resulting from a booking |
| Package | Individual physical parcel within a shipment |
| Facility | Warehouse/hub node in the network |
| Route | Fixed, reusable transport corridor between two facilities |
| Vehicle | Fleet asset (van, truck, aircraft) |
| Driver | Personnel operating vehicles |
| TransportLeg | Associative entity resolving Shipment ↔ Vehicle/Driver (N:M) |
| PackageFacilityTransit | Associative entity resolving Package ↔ Facility (N:M) |

Full reasoning behind every relationship, cardinality decision, and attribute choice is documented in [`docs/design_decisions.md`](docs/design_decisions.md).

## Database Migrations (Alembic)

This project uses Alembic for tracked, reversible schema migrations rather than direct `create_all()` calls, so schema changes are versioned and can be rolled back.

**Generate a new migration after changing models:**
```bash
alembic revision --autogenerate -m "describe your change"
```
Always review the generated file in `alembic/versions/` before applying it — autogenerate is not always perfect (e.g., it may not detect a column rename correctly).

**Apply migrations:**
```bash
alembic upgrade head
```

**Roll back the most recent migration:**
```bash
alembic downgrade -1
```

**Check current migration state:**
```bash
alembic current
```

Screenshots demonstrating the initial migration, upgrade, and downgrade cycle are available in [`docs/screenshots/`](docs/screenshots/).

## Test Instructions

```bash
pytest
```

*(Test suite is planned for a future phase — see Known Limitations.)*

## Example Usage

```python
from logistics_db.database import SessionLocal
from logistics_db.models import Client

with SessionLocal() as session:
    client = Client(
        name="Acme Corp",
        primary_email="ops@acme.com",
        phone_no="+1234567890",
        client_type="COMMERCIAL_ACCOUNT",
        billing_address_line1="100 Express Way",
        billing_city="Lagos",
        billing_country_code="NG",
    )
    session.add(client)
    session.commit()
```

## Known Limitations

- **Table population/seeding** was scoped out of this phase; planned for a future phase using `Faker` to generate realistic test data.
- **TrackingEvent** (granular scan-level event logging — barcode/RFID/GPS events) was considered but scoped out; `PackageFacilityTransit` currently captures only facility-level dwell time.
- **CHECK constraints** for status fields (e.g., `booking_status`, `payment_status`) are not yet database-enforced; allowed values are documented at the design level only.
- **Historical status tracking (SCD Type 2)** is not implemented; status fields reflect current state only.
- **`relationship()` ORM convenience methods** are not yet added; foreign key constraints are fully implemented at the database level, but Python-side object navigation (e.g., `payment.booking`) is not yet available.
- **Indexes** beyond automatic primary-key indexing are not yet added.
- **Stored procedures/functions** (optional bonus) are not yet implemented.
- **Automated test suite** (`pytest`) is not yet implemented.
- **Payment** is modeled as strictly 1:1 with `ShipmentBooking` for simplicity; a production system would likely need to support split/partial payments.

## Troubleshooting

**Postgres container fails to start with a `pg_ctlcluster` directory error:**
PostgreSQL 18's Docker image requires the volume to be mounted at `/var/lib/postgresql` rather than the older `/var/lib/postgresql/data` convention used in earlier major versions. This is reflected in `docker-compose.yml`.

**`ModuleNotFoundError` when running scripts:**
Ensure your virtual environment is activated (`source .venv/bin/activate`) and you're running commands from the project root.

**Alembic can't find the database, or `alembic upgrade` fails:**
Confirm the Docker container is running (`docker compose ps`) and `.env` values match your `docker-compose.yml` configuration. Confirm `alembic/env.py` correctly imports `settings` and `Base` and uses `settings.database_url()` in both `run_migrations_offline()` and `run_migrations_online()`.

**Alembic autogenerate doesn't detect an expected change:**
Ensure `src/logistics_db/models/__init__.py` imports every model class — a model that's never imported never registers with `Base.metadata`, so Alembic won't "see" it.

## Design Decisions

See [`docs/design_decisions.md`](docs/design_decisions.md) for full reasoning behind domain model choice, cardinality decisions, denormalization tradeoffs, naming conventions, and technology choices.

---

**Author:** Salome Gabriel (Sallie)
**Project:** Logistics Domain — Relational Database Design (DHL-style Carrier Model)
