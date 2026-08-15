# Design Decisions — DHL-Style Logistics Database

<div align="center">

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Normalization](https://img.shields.io/badge/Normalization-3NF-success)
![Status](https://img.shields.io/badge/Project-Week%203-blue)
![License](https://img.shields.io/badge/License-MIT-green)

*A well-organized database that stores information about a package delivery company, like DHL, FedEx, or UPS.*

</div>

---

# 📑 Table of Contents

- [What Is This Document?](#what-is-this-document)
- [What Was I Trying to Build?](#what-was-i-trying-to-build)
- [How to Set It Up Yourself](#how-to-set-it-up-yourself)
- [Why a Delivery Company and Not an Online Store?](#why-a-delivery-company-and-not-an-online-store)
- [WEEK 1 — Building the Tables and the Rules](#week-1--building-the-tables-and-the-rules)
- [WEEK 2 — Fixing the Fake Data and Writing Reports](#week-2--fixing-the-fake-data-and-writing-reports)
- [WEEK 3 — Still In Progress](#week-3--still-in-progress)
- [Tools I Used](#tools-i-used)
- [Docker Problems and Fixes](#docker-problems-and-fixes)
- [Problems I Ran Into (and How I Fixed Them)](#problems-i-ran-into-and-how-i-fixed-them)
- [What's Missing (On Purpose, For Now)](#whats-missing-on-purpose-for-now)
- [What's Next](#whats-next)

---

# What Is This Document?

> This explains **why** I made each choice — not just what the database looks like.
>
> A **database** is just a very organized set of tables (like spreadsheets) that store information and are connected to each other. Every table, every connection between tables, and every choice I made exists for a reason, explained below.

This document is split up **by week**, to match how the project was graded. Each week only talks about the decisions made during that week — later weeks just point back to earlier ones instead of repeating themselves. If you're grading this, the fastest way to check any specific deliverable is to look at the matching week's section below — each one tells you the exact file to open.

---

# What Was I Trying to Build?

I wanted to build a database (using **PostgreSQL**, a free and popular database program) that could store all the information a delivery company like DHL needs to run — packages, trucks, drivers, warehouses, and payments.

I cared most about:

- ✅ **Keeping data organized** (this is called "normalization" — it means not repeating the same information in multiple places by accident)
- ✅ **Making sure links between tables always make sense** (this is called "referential integrity" — for example, a package can't belong to a truck that doesn't exist)
- ✅ Making the database match how a real delivery company actually works
- ✅ Making it easy to add new things later without breaking everything
- ✅ Following good habits that professional database builders use

## The Tools Behind It

| Tool | What It's For, In Plain Words |
|---|---|
| PostgreSQL 18 | The actual database program that stores everything |
| SQLAlchemy 2.0 | Lets me write my tables as Python code instead of typing raw database commands |
| Alembic | Keeps a history of every change made to the table structure, so changes can be undone if something breaks |
| Pydantic Settings | Safely loads passwords and other secret settings from a file that never gets uploaded publicly |
| Docker | Runs the database in a self-contained "box" so I don't have to install it directly on my computer |
| `uv` | A fast tool for installing and managing the Python packages this project needs |
| DBeaver | A program with a visual interface for looking inside the database and running queries by hand |
| Faker + factory_boy | Two tools that work together to generate realistic-looking fake data (fake names, fake addresses, fake dates) for testing |
| pytest | A tool that automatically checks the code still works correctly (planned — see [Week 3](#week-3--still-in-progress)) |

---

# How to Set It Up Yourself

If you want to run this project on your own computer, here's the exact sequence:

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

python -m scripts.seed_all   # fills exchange_rates first, then all the fake data
```

A quick word on each step:

1. **Clone and enter the project folder** — grabs a copy of the code onto your computer.
2. **Create and activate a virtual environment** — a separate, clean space just for this project's Python packages, so they don't mix with anything else on your computer.
3. **`uv sync`** — installs every package the project needs, all at once.
4. **Copy the environment file** — `.env.example` is a template; copy it to `.env` and fill in your own database username/password so your real secrets never get uploaded to GitHub.
5. **`docker compose up -d`** — starts the PostgreSQL database inside its Docker "box," running quietly in the background.
6. **`alembic upgrade head`** — builds every table, in the correct order, up to the most current version.
7. **`python -m scripts.seed_all`** — fills the tables with realistic fake data. This is the **only** seeding command that should be run directly — it makes sure the currency lookup table is filled in first, before anything that depends on it.

**Settings you need to fill in:** `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB` — all explained with examples in `.env.example`.

---

# Why a Delivery Company and Not an Online Store?

## I Almost Copied an Online Store Design

At first, I looked at some example online-shopping datasets (like the kind used for Amazon or Shopify-style stores).

Those store databases are built around things like:

- Products for sale
- Sellers
- Orders
- Shopping carts
- Discounts
- Reviews

But that's not what a delivery company does. A delivery company doesn't sell products — it moves packages from one place to another for other companies and people. So I decided **not** to copy the online-store design, and instead built something that matches how a real delivery company actually operates.

A delivery company cares about completely different things than a store does.

```
Customer
    │
Books a Delivery
    │
Package Gets Picked Up
    │
Moves Through the Delivery Network
    │
Passes Through Warehouses
    │
Rides in Trucks/Planes
    │
Arrives at Recipient
```

An online store asks:

> "What did the customer buy?"

A delivery company asks:

> "Where is this package right now?"

That one difference changes everything about how the database needs to be built.

---

# WEEK 1 — Building the Tables and the Rules

**What this week covers, in one sentence:** figuring out what tables the database needs, connecting them to each other correctly, and adding rules that keep bad data out.

## The Main Tables (Entities)

A table in a database is basically like one spreadsheet tab. Each table stores one kind of thing. Here are all the tables (I call them "entities," which is just a fancy word for "a real-world thing the database tracks"):

| Table Name | What It Stores |
|----------|----------------|
| Client | A person or company involved in a delivery (they could be the sender, the receiver, or the one paying) |
| ShipmentBooking | A request from a customer to ship something |
| ServiceType | The kind of delivery speed being offered (like "Express" or "Standard") |
| Shipment | One actual physical delivery trip |
| Package | One box or parcel being sent |
| Facility | A warehouse or sorting hub |
| Route | A planned path a delivery can travel between two facilities |
| TransportLeg | One single stretch of a journey (like one flight or one truck ride) |
| Vehicle | A truck, van, or plane used to move packages |
| Driver | The person operating the vehicle |
| Payment | The money paid for a booking |
| PackageFacilityTransit | A record of a package passing through a warehouse |

There are **12 tables** total as of this week. I added `ServiceType` after some early feedback from my mentor. At first I was just going to store "Express" or "Standard" as a simple word inside the booking table. But a service type actually has its own details too (like how fast it promises to deliver), so it deserved its own table instead of just being a label.

*(A 13th table, `ExchangeRates`, gets added in Week 2 — see that section below.)*

## Picture of How Tables Connect

```text
                  +----------------+
                  |    Client      |
                  +----------------+
                    ▲   ▲    ▲
 sender_client_id   │   │    │ payer_client_id
 receiver_client_id │   │
                    │   │
            +---------------------+
            | ShipmentBooking     |
            +---------------------+
              │              │
              │one            │one
              │              │
             many│           one│
              ▼              ▼
      +-------------+    +---------+
      | Shipment    |    | Payment |
      +-------------+    +---------+
            │
            │one
            │
           many│
            ▼
      +-------------+
      | Package     |
      +-------------+
            │
            │
            │many
            │
            ▼
+--------------------------+
| PackageFacilityTransit   |
+--------------------------+
            ▲
            │
            │many
            │
            ▼
      +-------------+
      | Facility    |
      +-------------+

Shipment
     │
     │many
     ▼
TransportLeg
     ▲
     │
 Vehicle / Driver
```

The arrows show which table "points to" which other table, and whether it's a one-to-one connection or a one-to-many connection (meaning one row can be linked to several rows in another table).

## How the Tables Are Linked

### 1️⃣ Client → ShipmentBooking

**Something important:** The same Client can show up **three separate times** inside one single booking.

```
Client
   │
   ├── sender_client_id     (who's sending it)
   ├── receiver_client_id   (who's receiving it)
   └── payer_client_id      (who's paying for it)
```

These three are just different **jobs** the same Client can have — not three different types of people. I could have made separate tables called "Sender," "Receiver," and "Payer," but that would mean storing the same person's information over and over in multiple places. Instead, I just link back to the one Client table three different ways.

### 2️⃣ ShipmentBooking → Shipment

```
Booking
   │
   ├── Shipment (going to Abuja)
   ├── Shipment (going to Kano)
   └── Shipment (going to Port Harcourt)
```

One booking (one request from a customer) is *supposed* to be able to turn into several actual shipments — for example, if someone ships three boxes to three different cities in one order. That's how the connection is written in the Python code (`uselist=False` is set on the *reverse* direction, meaning "each shipment points back to just one booking"). But here's the honest part: **the database itself doesn't yet stop two shipments from pointing at the same booking in a way that breaks that intention** — I haven't added a rule to lock that down. It's on my known-gaps list below, with the fix already figured out.

### 3️⃣ ShipmentBooking → Payment

```
Booking
   │
   ▼
Payment
```

Each booking has exactly **one** payment, and the database enforces this — it will not allow two payments to attach to the same booking.

**Note for later:** In a real, fully-built system, this probably wouldn't be enough. Real companies usually need to handle paying in installments, refunds, different currencies, and partial payments. I kept it simple for now, but a real production system would need more than one payment per booking.

### 4️⃣ Shipment ↔ Vehicle

I didn't do this:

```
Shipment
    vehicle_id
```

That would only work if a package rode in exactly one vehicle for its whole journey — but packages usually switch trucks, planes, or vans along the way. So instead, I use a "middle" table:

```
Shipment
      │
      ▼
 TransportLeg
      ▲
      │
Vehicle
```

`TransportLeg` represents one single stretch of the trip — like "truck A carried it from the airport to the warehouse." A shipment can have many of these legs, each with a different vehicle and driver.

### 5️⃣ Package ↔ Facility

```
Package
    │
    ▼
PackageFacilityTransit
    ▲
    │
Facility
```

This "middle" table (called an **associative table** — a table whose whole job is just to connect two other tables together) stores when the package arrived at the warehouse (`inbound_timestamp`), when it left (`outbound_timestamp`), and which sorting lane it went through (`sorting_lane`). These pieces of information don't really belong to the Package by itself, or to the Facility by itself — they belong to the *event* of the package passing through that facility. That's why they live in their own table.

### 6️⃣ Route → Facility

```
Facility
     ▲
     │ starting point
 Route
     │ ending point
     ▼
Facility
```

This is the same trick as with Client above — one Facility table, used twice, for two different jobs (start and end point). The start and end aren't different kinds of things — they're just the same "Facility" concept playing two different roles on a given route.

## One Person, Many Roles

> [!TIP]
> One table.
>
> Many different jobs.

A Client can be the sender today, the receiver tomorrow, and the one paying next week. It's still the same person or company in the Client table. Giving them different "roles" (jobs) instead of separate tables keeps the database clean and avoids storing the same information multiple times.

## Giving Every Table Its Own ID Name

At first, every table just had a column called `id` to identify each row. I changed this so each table's ID has its own specific name instead — like `client_id`, `payment_id`, `leg_id`, and `transit_id`.

**Why this matters:** When you combine information from several tables at once (this is called a **JOIN** — a way of pulling matching rows together from two or more tables), it gets confusing fast if every table just says "id." Having `client_id` clearly tells you it's the Client's ID, no matter which table you're looking at.

I applied this change across all 12 tables and updated every place that pointed to those IDs.

## On-Purpose Repeated Information

Normally, repeating information in a database is something to avoid. But sometimes it's actually a smart trade-off. I did this twice, on purpose, for good reasons.

**Payment Also Stores Who Paid.** The Payment table has a `payer_client_id` column, even though you could already figure out who paid by following `Payment → ShipmentBooking → Client`. I added it directly to Payment anyway, so I can quickly answer questions like *"show me every payment Client X has ever made"* without having to connect three tables together every time. I thought about storing the payer's actual name directly on the Payment table instead of just their ID — I decided against that, because if the client ever changes their name, old payments wouldn't update and would show the wrong name. Storing just the ID avoids that problem, since the ID always points to the client's current information.

*(Heads up — this is one of the two spots where I found a seed-data bug during Week 2. See [Week 2](#week-2--fixing-the-fake-data-and-writing-reports) below for how it got fixed.)*

**Shipment Also Stores Where It Starts and Ends.** The Shipment table stores `origin_facility_id` and `destination_facility_id`, even though this could technically be figured out by following `Shipment → TransportLeg → Route → Facility`. This one is even safer than the payment example above, because a shipment's starting point and ending point are decided the moment it's created and never change. So there's no risk of it ever going "out of date," and it saves having to connect multiple tables together just to find out where a package is headed.

## Naming Things and Choosing Data Types

**Better naming.** `sortation_lane` became `sorting_lane`. A small change, but plain English is easier to read than jargon.

**Using the right kind of number.** For money and measurements (like package dimensions), I used a data type called `NUMERIC` (also called `DECIMAL`) instead of `FLOAT`. Both store numbers, but `FLOAT` can sometimes round numbers slightly wrong — which is a real problem when you're dealing with money or exact measurements. `NUMERIC` keeps the numbers exact.

**Timezones.** Every timestamp that tracks something happening in the real world (like when a package arrived) uses a data type called `TIMESTAMP WITH TIME ZONE`. Regular timestamps don't remember which timezone they were recorded in, which causes confusion for a company operating across the whole world. `TIMESTAMP WITH TIME ZONE` keeps track of the timezone, so times are never mixed up.

## Rules That Block Bad Values (CHECK Constraints)

Six status columns in this database should only ever hold specific words — for example, `booking_status` should only ever be "pending," "confirmed," or a handful of other allowed values, never a random typo. I added a rule called a **CHECK constraint** (a rule built directly into the database that rejects any data that doesn't match a list of allowed values) for all six of them: `chk_booking_status`, `chk_payment_status`, `chk_shipment_status`, `chk_leg_status`, `chk_driver_operational_status`, and `chk_vehicle_operational_status`.

I tested this live in DBeaver by trying to insert a made-up `booking_status` value that isn't on the allowed list — PostgreSQL rejected it, exactly as expected.

**A tool limitation I ran into:** Alembic normally has a feature that can look at my Python code and automatically write the migration file for me ("autogenerate"). It turns out the version of Alembic this project uses (1.18.5) doesn't support autogenerating CHECK constraints yet — that feature wasn't added until a later version (1.19.0). I confirmed this in Alembic's own documentation. So instead of relying on the automatic tool, I wrote all six constraints by hand using a command called `op.create_check_constraint()`.

## Rules That Speed Up Searching (Indexes)

An **index** is like the index at the back of a book — instead of the database reading through every single row to find what it's looking for, it can jump straight to the right spot. I added twenty indexes: one on every foreign key column (the columns that link one table to another), plus one on `payments.transaction_timestamp`, since I knew Week 2 and 3 reports would need to filter and sort payments by date. Unlike the CHECK constraints above, Alembic's autogenerate tool worked fine for detecting these, so those migrations were generated automatically rather than written by hand.

## What Kind of Database Is This?

This project is a **relational database** — a normal database made of connected tables, built to run a real system day-to-day (this is sometimes called "OLTP," short for a system that handles everyday transactions). It is **not** a "dimensional model," which is a different kind of database built specifically for big-picture reporting and analytics (using ideas like "facts" and "dimensions").

The rule I followed to keep the tables organized (called "3NF," or Third Normal Form — basically a checklist for avoiding repeated or badly organized data) is a relational-database idea. "Facts" and "dimensions" are a completely different, analytics-only idea, and they don't apply here. One later feature — a "materialized view" (basically a saved, ready-made report that doesn't need to be recalculated every time) added in Week 2 — is just a performance shortcut built on top of this same relational database. It doesn't mean the whole database changed into a different kind of system.

## Week 1 Files, For the Grader

| What | Where to Find It |
|---|---|
| Picture of the whole database (ERD) | `docs/erd.png` |
| The reasoning above, in this same document | Everything under this "WEEK 1" heading |
| The actual table definitions, written in Python | `src/logistics_db/models/` (one file per table) |
| Database connection settings | `src/logistics_db/database.py`, `src/logistics_db/config.py` |
| The migration that builds every table for the first time | `alembic/versions/` — labeled `"create initial logistics schema"` |
| The hand-written CHECK constraints migration | `alembic/versions/` — labeled `"added check constraints on status field"` |
| The indexes migration | `alembic/versions/` — labeled `"add indexes to foreign key columns and payment timestamp"` |
| Docker setup | `docker-compose.yml` |
| Screenshots | **Not attached yet.** Instead, everything can be checked live — run `alembic history --verbose` to see every change applied in order, and `alembic current` to confirm the database is fully up to date. |

---

# WEEK 2 — Fixing the Fake Data and Writing Reports

**What this week covers, in one sentence:** giving the tables more real-world detail, rebuilding how fake test data gets generated (and fixing bugs in it), and writing SQL reports a real logistics company might actually ask for.

## Giving Tables More Real-World Detail

Based on more feedback from my mentor, I went back and added realistic detail to several tables:

**Client** got a client type, a full billing address (street, city, state, zip/postal code, country), and a "when were they added" timestamp. I also renamed `email` to `primary_email`, in case a client ends up needing more than one email someday. I left out tax ID numbers and account numbers on purpose — not needed at this stage. I also left out things like gender or age, which showed up in a reference online-store dataset I looked at, but don't actually matter for a company that ships packages for businesses.

**Payment** got a `currency_code` (which currency was used), a `payment_type`, a `payment_method`, and a `payment_reference` (an ID from an outside payment company, like a receipt number — allowed to be empty since not every payment has one right away), and a `transaction_timestamp` that the database fills in automatically the moment the row is created, so it's always accurate no matter what app or script inserted the data.

**Shipment** now also tracks its starting warehouse, ending warehouse, expected delivery date, actual delivery date, and when it was created — which helps answer "was this delivered on time?"

**Package** now also tracks its size (length, width, height, needed to price shipping by size and not just weight), a scannable tracking code (like a barcode), and whether it contains hazardous materials, so it can be handled carefully.

**Facility** now has a short code (like an airport code), a full address, GPS coordinates, and whether it's a certified secure facility. **Route** now has a short code, an expected number of hours to complete the trip, and whether it's currently active or retired. **Vehicle** now has an ID number (a VIN for trucks, or a tail number for planes), how much cargo space it has, and its current status. **Driver** now has an employee number, phone number, license expiration date, and current status.

## A New Table: ExchangeRates

I added a 13th table, `ExchangeRates`, purely as a **reference/lookup table** — a small table of settled, mostly-unchanging facts (in this case, how much one US Dollar, Euro, or British Pound is worth in Nigerian Naira). It's different from every other table in one important way: it doesn't get wiped and refilled every time I regenerate fake data. It gets its own values loaded in separately (this is called "upserting" — updating a row if it exists, or adding it if it doesn't).

```python
class ExchangeRates(Base):
    __tablename__ = "exchange_rates"
    currency_code: Mapped[str] = mapped_column(String(3), primary_key=True)
    rate_to_ngn: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
```

I also changed `Payment.currency_code` from a plain 3-letter text field into a real foreign key pointing at `exchange_rates.currency_code`, so a payment can never reference a currency the database doesn't actually know the exchange rate for. Making that change meant I had to empty out a few dependent tables once (`payments`, `shipments`, `package_facility_transits`, `transport_legs`), since some existing rows had currency codes with no matching row in the new `exchange_rates` table yet. This was applied in migration `e39f3d5451ad — "add exchange_rates table"`.

**Table count: 13** as of this week.

## Adding the Relationship Layer

I also went back and added `relationship()` connections across the whole schema (Client-to-booking by role, service type to booking, booking to payment, booking to shipment, and more). I had deliberately skipped this in Week 1, since none of the Week 1 SQL work needed it. It became necessary once I started using `factory_boy`'s `SubFactory` feature for generating realistic fake data — that feature needs the ORM-level relationship connections, not just the raw foreign key columns underneath them.

## Rebuilding How Fake Data Gets Generated

I rebuilt the fake-data-generating scripts using **Faker** (generates realistic fake values like names and addresses) plus **factory_boy** (a tool that builds those fake values into proper, connected database rows), and reorganized everything into a proper package:

```
scripts/
├── __init__.py
├── seed_reference_data.py   # fills exchange_rates — the static lookup values
├── seed_data.py             # the main bulk fake-data generator
└── seed_all.py              # the one script you should actually run — runs things in the right order
```

**There is only one supported way to run this:** `python -m scripts.seed_all`, from the project's root folder. That script fills `exchange_rates` first, *then* generates all the bulk fake data — because `payments.currency_code` now depends on `exchange_rates` already existing (see above).

### Making Timestamps Make Sense

My early fake data generated every date and time completely independently and randomly, which created some impossible situations — a shipment created *before* its own booking existed, or a package scanned into a warehouse before its shipment was even created. I fixed this by making every timestamp flow logically from its "parent" event, top to bottom:

| Field | Based On | How Far After |
|---|---|---|
| `Client.created_at` | a fixed window | 6 to 18 months ago |
| `ShipmentBooking.created_at` | — | anywhere from 6 months ago to now |
| `Payment.transaction_timestamp` | the booking's `created_at` | 1–72 hours later, never after right now |
| `Shipment.created_at` | the booking's `created_at` | 1–48 hours later, never after right now |
| `Shipment.estimated_delivery_date` | the shipment's `created_at` | 1–10 days later (in the future — that's correct, it's just an estimate) |
| `Shipment.actual_delivery_date` | the shipment's `created_at`, only if it was actually delivered | 1–12 days later, never after right now |
| `PackageFacilityTransit.inbound_timestamp` | the shipment's `created_at` | 1–96 hours later, never after right now |
| `PackageFacilityTransit.outbound_timestamp` | its own `inbound_timestamp` | 1–48 hours later |

This fix also turned out to matter for one of the reports below (Task 4, month-over-month revenue growth): before this fix, every payment shared the same "right now" timestamp, so there was no way to compare one month against another. Spreading booking dates out across a 6-month window fixed that too.

**Timezones, again.** Every `datetime.now()` call in the code got changed to `datetime.now(timezone.utc)`, and every Faker date/time value got a `tzinfo=timezone.utc` attached, so nothing ever accidentally mixes a "timezone-aware" time with a "timezone-naive" one — which Python would otherwise refuse to compare and throw an error on.

### Two Bugs I Found and Fixed

While testing the reports below, I found two real bugs in my own fake-data generator:

1. **Payment's "who paid" didn't match the booking's "who paid."** The original factory picked a completely random, unrelated client as the payer on every Payment row, instead of reusing the actual payer from that payment's booking — quietly breaking the on-purpose repeated information I set up in Week 1 (see [above](#on-purpose-repeated-information)). I caught this because Task 1 below (a report that joins Payment and ShipmentBooking on "who paid") only returned 35 rows instead of the roughly 2,500 I expected. I fixed it by telling the factory to reuse the booking's actual payer, then regenerated the `payments` table.
2. **Fake emails weren't guaranteed unique.** `Client.primary_email` has a rule in the database saying no two clients can share an email, but the fake-data generator had no way of guaranteeing that — it collided once I got to around 100 fake clients. I fixed it by attaching a guaranteed-unique counter to every generated email.

## The Reports (SQL Tasks)

Before any of these can run, `scripts/payments_view_table.sql` needs to be run first — it builds a helper view that converts every payment's amount into Naira using the `exchange_rates` table, so spending figures are comparable no matter what currency a payment was originally made in. Tasks 1, 3, and 4 below all depend on this view; Task 2 does not.

**Task 1 — Customers Who Order a Lot.** Adds up each client's bookings (using the direct `Payment.payer_client_id` link from Week 1), only counting `CONFIRMED` bookings, and only keeps clients with 5 or more of them. The "big spender" cutoff isn't a hardcoded dollar amount — it's calculated fresh every time, by averaging what every client has spent and using that as the bar. → `scripts/week_2_task_1.sql`

**Task 2 — On-Time vs. Delayed Deliveries, by City.** Compares each destination city's shipments to see how many arrived on time versus late. → `scripts/week_2_task_2.sql`

**Task 3 — Monthly Spending Per Client (Saved Report).** Built as a **materialized view** — a saved, ready-made report that doesn't need to be recalculated from scratch every single time someone looks at it. It's named `mv_client_monthly_spend_summary` rather than `mv_customer_monthly_spend_summary` (the wording used in the original assignment) on purpose — my actual table is called `Client`, not `Customer`, so the view name matches the real table it's built on. I just refer to my customers as "clients" throughout this whole project, to stay consistent with the schema. → `scripts/week_2_task_3.sql`

**Task 4 — Month-over-Month Revenue Growth.** Compares total revenue from one month to the next, made possible by the timestamp fix described above. → `scripts/week_2_task_4.sql`

**About screenshots this week:** instead of attaching a picture of each result, I'm relying on the `.sql` files themselves as proof — anyone can run them directly against the seeded database and get the exact same result I got.

## Known Gaps From Earlier — Now Resolved

Week 2 originally left four data-model gaps flagged but unfixed. All four have since been resolved:

- **A shipment's `booking_id` is now locked to "only one shipment per booking."** Added a `unique=True` rule (via migration) plus cleaned up any duplicate `booking_id` values left over from earlier, more randomized fake-data generation.
- **The fake-data generator now creates one shipment for every eligible booking**, instead of the original `random.choice()` approach that only produced 15 shipments total. Bookings that are `PENDING` or `CANCELLED` are skipped, since those wouldn't realistically have a shipment yet.
- **`CANCELLED` is now included** in the list of values the fake-data generator can pick for `booking_status`, matching what the database's CHECK constraint already allowed.
- **A shipment's status is now derived from its booking's status**, instead of being generated independently — so a `DELIVERED` booking can no longer end up paired with a `pending` shipment.

## Week 2 Files, For the Grader

| What | Where to Find It |
|---|---|
| Loads the currency lookup values | `scripts/seed_reference_data.py` |
| Generates all the bulk fake data | `scripts/seed_data.py` |
| The one script to actually run | `scripts/seed_all.py` — run with `python -m scripts.seed_all` |
| The new `ExchangeRates` table + its migration | `src/logistics_db/models/exchange_rates.py`; migration `e39f3d5451ad — "add exchange_rates table"` |
| Helper view (Naira conversion), used by most tasks below | `scripts/payments_view_table.sql` |
| Task 1 — Big-spending, repeat customers | `scripts/week_2_task_1.sql` |
| Task 2 — On-time vs. delayed deliveries | `scripts/week_2_task_2.sql` |
| Task 3 — Saved monthly-spend report | `scripts/week_2_task_3.sql` |
| Task 4 — Month-over-month revenue growth | `scripts/week_2_task_4.sql` |

**To check Week 2 live:** run `python -m scripts.seed_all`, then run each `.sql` file above in DBeaver against the `logistics_db` database.

---

# WEEK 3 — Still In Progress

This week's focus is on making the code that *talks to* the database better organized (a pattern called the **Repository Pattern** — basically, keeping all the database-reading-and-writing code in one clean, reusable place instead of scattered everywhere), making slow queries faster, and adding proper transaction logic (making sure a group of related database changes either *all* happen together, or *none* of them do — so nothing gets left half-done).

| Task | Status |
|---|---|
| Task 1 — Measuring and speeding up slow queries (using a tool called `EXPLAIN ANALYZE`, which shows exactly how PostgreSQL is running a query, plus adding new indexes where needed) | *Not finished yet* |
| Task 2 — Repository Pattern, safe transaction handling, logging, and automated tests (`pytest`) | *Not finished yet* |
| Task 3 — A `process_shipment` method (owned by teammate Salome) | *Not finished yet* |

This section will get filled in with exact file paths for each piece as it's completed.

---

# Tools I Used

| Tool | Why I Chose It |
|------------|--------|
| PostgreSQL 18 | A free, powerful, and current database program |
| Docker | Lets me run the database in a self-contained "box" on my computer, so I don't have to install it directly — especially helpful since my laptop has limited disk space and runs two operating systems side by side |
| SQLAlchemy 2.0 | A tool that lets me write database tables using Python code instead of writing raw database commands by hand |
| Alembic | Keeps a history of every change I make to the database structure, so I can undo changes if something breaks |
| pydantic-settings | Safely loads settings (like passwords) from a separate file, so secret information never gets accidentally uploaded to a public code repository |
| `uv` | A fast, modern tool for installing and managing this project's Python packages |
| DBeaver | A visual program for peeking inside the database and running queries by hand, without writing a script |
| Python Faker + factory_boy | Two tools that work together to generate realistic fake test data — Faker makes up realistic values, factory_boy wires them together into properly connected rows |
| pytest | A tool that will automatically check the code keeps working correctly (planned for Week 3) |

---

# Docker Problems and Fixes

## Why Use Docker At All

I chose to run PostgreSQL inside Docker (instead of installing it directly on my computer) so I could easily recreate the exact same setup on any machine, without cluttering my actual computer — which mattered a lot since I'm short on disk space and running two operating systems on the same laptop.

## The Folder Location Problem

Older tutorials tell you to save your database files at this folder:

```yaml
/var/lib/postgresql/data
```

But PostgreSQL 18 needed the files saved here instead:

```yaml
/var/lib/postgresql
```

This changed because of updates related to a tool called `pg_ctlcluster` (a program that manages PostgreSQL "behind the scenes").

> [!CAUTION]
> Because I didn't know about this change at first, my database container kept failing to start — until I found and fixed the folder path. It's already corrected in `docker-compose.yml`, so this won't happen to anyone else running the project.

---

# Problems I Ran Into (and How I Fixed Them)

A few other snags, beyond the Docker one above, in case someone else runs into the same thing:

**"`alembic upgrade` fails with a currency error."** This happens if you try to reseed the database *after* the `exchange_rates` table was added, but you run `seed_data.py` directly instead of going through `seed_all.py`. Fix: always use `python -m scripts.seed_all` — it loads the currency values first, in the right order.

**"Alembic didn't generate a migration for my new rule."** As explained in the Week 1 section above, the version of Alembic this project uses can't automatically detect new CHECK constraints — that feature was added in a newer version than what's installed here. The fix is to write that one migration by hand using `op.create_check_constraint()`, which is exactly what I did.

---

# What's Missing (On Purpose, For Now)

Things I've chosen not to build yet, and why:

- **A detailed log of every single scan** (`TrackingEvent`) — every individual barcode scan or GPS ping. Right now, `PackageFacilityTransit` only tracks how long a package stayed at one warehouse overall, not every individual scan along the way.
- **GPS location pings, RFID scans** (a wireless tracking technology some warehouses use), and **individual barcode scan events** — same reasoning as above.
- **A full history of status changes.** Right now, when a shipment's status changes from "in transit" to "delayed," the old value is simply overwritten and lost — there's no record of when the change happened or what it used to say. Keeping that history (sometimes called "SCD Type 2" in database terminology) would be a great feature to add later, since it would help a lot with tracking down problems after the fact.
- **Stored procedures** (small pieces of reusable code saved and run directly inside the database itself) — this was an optional bonus, not done yet.
- **A full automated test suite** using `pytest` — in progress as of Week 3, not finished yet.
- **Convenience shortcuts in the code for navigating between connected tables** — the actual database connections are all there; this would just be an extra layer that makes the Python code nicer to write.

These are all planned for a later phase of the project.

---

# What's Next

## Planned for Later

- Finishing Week 3: measuring and speeding up slow queries, building out the Repository Pattern, adding safe transaction handling, and writing automated tests
- Keeping a full history of status changes, not just the current one
- Adding stored procedures and a full `pytest` test suite

---

<div align="center">

**Salome Gabriel (Sallie)**

*Project: Logistics Domain — Relational Database Design (DHL-Style Carrier Model)*

</div>
