# Logistics Database — DHL-Style Carrier Model

A normalized PostgreSQL relational database modeling express carrier logistics operations, built with SQLAlchemy ORM and managed via Alembic migrations.

> **For the grader:** this README is organized by week. Each week's section lists exactly what was delivered and the exact file path to find it. Full reasoning for every design decision is in [`docs/design_decisions.md`](docs/design_decisions.md), which is organized the same way.

---

## Tech Stack

PostgreSQL 18 (Docker) · SQLAlchemy 2.0 · Alembic · Pydantic Settings · `uv` · DBeaver · Faker + factory_boy · pytest

## Setup Instructions

```bash
git clone https://github.com/Sallie25/logistics_db_project.git
cd logistics_db_project

uv venv --python 3.13
source .venv/bin/activate
uv sync

cp .env.example .env   # fill in your own values

docker compose up -d
docker compose ps

alembic upgrade head

python -m scripts.seed_all   # seeds exchange_rates first, then bulk fake data
```

## Environment Variables

See `.env.example`. Requires `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`.

---

## WEEK 1 Deliverables — Schema Design, Migrations, Constraints, Indexes

| Deliverable | File / Location |
|---|---|
| ERD (12 entities, PK/FK/associative tables/cardinality) | `docs/erd.png` |
| Design reasoning (domain choice, cardinality decisions, denormalization) | `docs/design_decisions.md` § WEEK 1 |
| SQLAlchemy models | `src/logistics_db/models/` (one file per entity) |
| Database connection / config | `src/logistics_db/database.py`, `src/logistics_db/config.py` |
| Initial Alembic migration (schema creation) | `alembic/versions/` — migration message `"create initial logistics schema"` |
| CHECK constraints migration (hand-written, see design doc §6 for why) | `alembic/versions/` — migration message `"added check constraints on status field"` |
| Indexes migration | `alembic/versions/` — migration message `"add indexes to foreign key columns and payment timestamp"` |
| Docker / Postgres setup | `docker-compose.yml` |
| Screenshots | **Not currently attached** — see `docs/design_decisions.md` § WEEK 1 note; migration state can be reproduced and verified live via `alembic current` / `alembic history --verbose` |

**To verify Week 1 live:** run `alembic history --verbose` to see all applied migrations in order, and `alembic current` to confirm the schema is at `head`.

---

## WEEK 2 Deliverables — Seed Data Overhaul, Reporting Queries

| Deliverable | File / Location |
|---|---|
| Reference data seeding (`exchange_rates`) | `scripts/seed_reference_data.py` |
| Bulk fake data seeding (Faker + factory_boy, all entities) | `scripts/seed_data.py` |
| Seed orchestrator (**run this one — enforces correct order**) | `scripts/seed_all.py` — run via `python -m scripts.seed_all` |
| `ExchangeRates` model + migration | `src/logistics_db/models/exchange_rates.py`; migration `e39f3d5451ad — "add exchange_rates table"` |
| Design reasoning (timestamp coherence, seed data bug fixes, denormalization follow-up) | `docs/design_decisions.md` § WEEK 2 |
| Helper view — converts `payments.amount` into Naira using `exchange_rates`, used by every task below | `scripts/payments_view_table.sql` |
| **Task 1** — Customer order history aggregation (5+ orders, dynamic avg-spend threshold) | `scripts/week_2_task_1.sql` |
| **Task 2** — On-time vs delayed shipments per destination city | `scripts/week_2_task_2.sql` |
| **Task 3** — Materialized view for monthly spend by client | `scripts/week_2_task_3.sql` — ⚠️ currently named `mv_client_monthly_spend_summary`; task spec asked for `mv_customer_monthly_spend_summary` — confirm with supervisor whether a rename is required. The required refresh command (as a comment below the view) is also not yet added to this file. |
| **Task 4** — Month-over-Month revenue growth | `scripts/week_2_task_4.sql` |

**Run order for Week 2 SQL files:** `payments_view_table.sql` must be run first — it creates the `payments_view` that Tasks 1, 3, and 4 all depend on (it converts every payment's amount into Naira using the `exchange_rates` table, so spend figures are comparable across currencies). Task 2 does not depend on the view.

**Note on screenshots:** per project decision, Week 2 tasks are evidenced by runnable `.sql` files rather than screenshots — each can be executed directly against the seeded database to reproduce the exact result shown during review.

**To verify Week 2 live:** `python -m scripts.seed_all`, then run each `.sql` file listed above in DBeaver against the `logistics_db` database.

---

## WEEK 3 Deliverables — Repository Pattern, Query Optimization, Transaction Logic

*(In progress — this section will list exact file paths for the Repository class, EXPLAIN ANALYZE before/after evidence, pytest integration tests, and the `process_shipment` method as each is completed.)*

| Deliverable | File / Location |
|---|---|
| Task 1 — EXPLAIN ANALYZE + index optimization | *TBD* |
| Task 2 — Repository Pattern, session/transaction handling, logging, pytest integration tests | *TBD* |
| Task 3 — `process_shipment` method (Salome) | *TBD* |

---

## Architecture Overview

```
Client (sender/receiver/payer roles)
   │
ShipmentBooking ──1:1── Payment ──N:1── ExchangeRates (currency lookup)
   │        └──N:1── ServiceType
   │ 1:N (intended; see Known Gaps below)
   ▼
Shipment ──1:N── Package
   │
TransportLeg ──N:1── Vehicle / Driver / Route ──N:1── Facility

Package ──N:M (via PackageFacilityTransit)── Facility
```

13 entities total (12 from Week 1 + `ExchangeRates` added Week 2). Full entity table in `docs/design_decisions.md` § WEEK 1 §2.

## Known Limitations / Open Items

See `docs/design_decisions.md` § WEEK 2 §7 for the current list of flagged-but-unresolved schema gaps (`Shipment.booking_id` uniqueness enforcement, shipment-generation coverage, `booking_status`/`shipment_status` consistency). Also see § WEEK 1 for Week-1-scoped items (CHECK constraints on all status fields — done; historical status tracking / SCD Type 2 — not implemented; stored procedures — not yet implemented; `pytest` suite — in progress as of Week 3).

## Troubleshooting

**Postgres container fails to start with a `pg_ctlcluster` error:** PostgreSQL 18 requires the Docker volume mounted at `/var/lib/postgresql`, not `/var/lib/postgresql/data`. Already reflected in `docker-compose.yml`.

**`alembic upgrade` fails with a currency FK violation:** if reseeding after the `exchange_rates` migration, ensure `python -m scripts.seed_all` is used (not `seed_data.py` directly) — it loads reference data first.

**Alembic autogenerate produces an empty migration for a new CHECK constraint:** this project uses Alembic 1.18.5, which does not support CHECK constraint autogenerate detection (added in 1.19.0). Write the migration by hand using `op.create_check_constraint()`.

---

**Author:** Salome Gabriel (Sallie)
**Project:** Logistics Domain — Relational Database Design (DHL-style Carrier Model)
