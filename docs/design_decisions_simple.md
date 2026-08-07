# Design Decisions — DHL-Style Logistics Database

<div align="center">

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Normalization](https://img.shields.io/badge/Normalization-3NF-success)
![Status](https://img.shields.io/badge/Project-Week%201-blue)
![License](https://img.shields.io/badge/License-MIT-green)

*A well-organized database that stores information about a package delivery company, like DHL, FedEx, or UPS.*

</div>

---

# 📑 Table of Contents

- [What Is This Document?](#what-is-this-document)
- [What Was I Trying to Build?](#what-was-i-trying-to-build)
- [Why a Delivery Company and Not an Online Store?](#why-a-delivery-company-and-not-an-online-store)
- [The Main Tables (Entities)](#the-main-tables-entities)
- [Picture of How Tables Connect](#picture-of-how-tables-connect)
- [How the Tables Are Linked](#how-the-tables-are-linked)
- [One Person, Many Roles](#one-person-many-roles)
- [Giving Every Table Its Own ID Name](#giving-every-table-its-own-id-name)
- [On-Purpose Repeated Information](#on-purpose-repeated-information)
- [Adding More Details to Tables](#adding-more-details-to-tables)
- [Naming Things and Choosing Data Types](#naming-things-and-choosing-data-types)
- [Only Keeping the Current Status](#only-keeping-the-current-status)
- [Rules I Didn't Add Yet](#rules-i-didnt-add-yet)
- [One Kind of Database, Not Two](#one-kind-of-database-not-two)
- [What's Missing (On Purpose, For Now)](#whats-missing-on-purpose-for-now)
- [Tools I Used](#tools-i-used)
- [Docker Problems and Fixes](#docker-problems-and-fixes)
- [What's Next](#whats-next)
- [What I Learned](#what-i-learned)

---

# What Is This Document?

> This explains **why** I made each choice — not just what the database looks like.
>
> A **database** is just a very organized set of tables (like spreadsheets) that store information and are connected to each other. Every table, every connection between tables, and every choice I made exists for a reason, explained below.

---

# What Was I Trying to Build?

I wanted to build a database (using **PostgreSQL**, a free and popular database program) that could store all the information a delivery company like DHL needs to run — packages, trucks, drivers, warehouses, and payments.

I cared most about:

- ✅ **Keeping data organized** (this is called "normalization" — it means not repeating the same information in multiple places by accident)
- ✅ **Making sure links between tables always make sense** (this is called "referential integrity" — for example, a package can't belong to a truck that doesn't exist)
- ✅ Making the database match how a real delivery company actually works
- ✅ Making it easy to add new things later without breaking everything
- ✅ Following good habits that professional database builders use

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

# The Main Tables (Entities)

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

There are **12 tables** total. I added `ServiceType` after my first week of work, based on feedback from my mentor. At first I was just going to store "Express" or "Standard" as a simple word inside the booking table. But a service type actually has its own details too (like how fast it promises to deliver), so it deserved its own table instead of just being a label.

---

# Picture of How Tables Connect

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

---

# How the Tables Are Linked

## 1️⃣ Client → ShipmentBooking

**Something important:** The same Client can show up **three separate times** inside one single booking.

```
Client
   │
   ├── sender_client_id     (who's sending it)
   ├── receiver_client_id   (who's receiving it)
   └── payer_client_id      (who's paying for it)
```

These three are just different **jobs** the same Client can have — not three different types of people.

I could have made separate tables called "Sender," "Receiver," and "Payer," but that would mean storing the same person's information over and over in multiple places. Instead, I just link back to the one Client table three different ways.

---

## 2️⃣ ShipmentBooking → Shipment

```
Booking
   │
   ├── Shipment (going to Abuja)
   ├── Shipment (going to Kano)
   └── Shipment (going to Port Harcourt)
```

One booking (one request from a customer) can turn into several actual shipments — for example, if someone ships three boxes to three different cities in one order.

---

## 3️⃣ ShipmentBooking → Payment

Right now:

```
Booking
   │
   ▼
Payment
```

Each booking has exactly **one** payment.

**Note for later:** In a real, fully-built system, this probably wouldn't be enough. Real companies usually need to handle:

- Paying in installments (a little at a time)
- Refunds
- Different currencies
- Partial payments (paying only part of the cost)

I kept it simple for now, but a real production system would need more than one payment per booking.

---

## 4️⃣ Shipment ↔ Vehicle

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

---

## 5️⃣ Package ↔ Facility

```
Package
    │
    ▼
PackageFacilityTransit
    ▲
    │
Facility
```

This "middle" table (called an **associative table** — a table whose whole job is just to connect two other tables together) stores:

- When the package arrived at the warehouse (`inbound_timestamp`)
- When it left the warehouse (`outbound_timestamp`)
- Which sorting lane it went through (`sorting_lane`)

These pieces of information don't really belong to the Package by itself, or to the Facility by itself — they belong to the *event* of the package passing through that facility. That's why they live in their own table.

---

## 6️⃣ Route → Facility

```
Facility
     ▲
     │ starting point
 Route
     │ ending point
     ▼
Facility
```

This is the same trick as with Client above — one Facility table, used twice, for two different jobs (start and end point).

---

# One Person, Many Roles

> [!TIP]
> One table.
>
> Many different jobs.

A Client can be:

- The sender today
- The receiver tomorrow
- The one paying next week

It's still the same person or company in the Client table. Giving them different "roles" (jobs) instead of separate tables keeps the database clean and avoids storing the same information multiple times.

---

# Giving Every Table Its Own ID Name

At first, every table just had a column called `id` to identify each row. I changed this so each table's ID has its own specific name instead — like `client_id`, `payment_id`, `leg_id`, and `transit_id`.

**Why this matters:** When you combine information from several tables at once (this is called a **JOIN** — a way of pulling matching rows together from two or more tables), it gets confusing fast if every table just says "id." Having `client_id` clearly tells you it's the Client's ID, no matter which table you're looking at.

I applied this change across all 12 tables and updated every place that pointed to those IDs.

---

# On-Purpose Repeated Information

Normally, repeating information in a database is something to avoid. But sometimes it's actually a smart trade-off. I did this twice, on purpose, for good reasons.

## Payment Also Stores Who Paid

The Payment table has a `payer_client_id` column, even though you could already figure out who paid by following `Payment → ShipmentBooking → Client`.

I added it directly to Payment anyway, so I can quickly answer questions like *"show me every payment Client X has ever made"* without having to connect three tables together every time. This matters for reports I need to build later.

I thought about storing the payer's actual name directly on the Payment table instead of just their ID. I decided against that — if the client ever changes their name, the old copy stored on old payments wouldn't update, and it would show the wrong name. Storing just the ID avoids that problem, since the ID always points to the client's current information.

## Shipment Also Stores Where It Starts and Ends

The Shipment table stores `origin_facility_id` and `destination_facility_id` (the starting and ending warehouse), even though this could technically be figured out by following `Shipment → TransportLeg → Route → Facility`.

This one is even safer than the payment example above, because a shipment's starting point and ending point are decided the moment it's created and never change. So there's no risk of it ever going "out of date" — and it saves having to connect multiple tables together just to find out where a package is headed.

---

# Adding More Details to Tables

Based on feedback from my mentor, I added more real-world details to several tables.

## Client

I gave Client more realistic information:

- **Added:** what type of client they are, their billing address (street, city, state, zip/postal code, country), and when they were created
- **Renamed:** `email` became `primary_email` (clearer, in case a client has more than one email someday)
- **Left out on purpose:** tax ID numbers and account numbers — not needed for this stage of the project
- **Left out on purpose:** things like gender or age, which showed up in some example datasets I looked at, but don't actually matter for a company that ships packages for businesses

## Payment

I made Payment feel more like a real financial record:

- `currency_code` — which currency was used (like USD or NGN), stored as flexible text so I can support more currencies later without changing the database
- `payment_type`, `payment_method`, and `payment_reference` — the reference is an ID from an outside payment company (like a receipt number), and it's allowed to be empty since not every payment has one right away
- `transaction_timestamp` — the exact time the payment happened, automatically filled in by the database itself (not by whatever app or script inserts the data), so it's always accurate

## Shipment & Package

Shipment now also tracks: starting warehouse, ending warehouse, expected delivery date, actual delivery date, and when it was created. This helps answer questions like "was this delivered on time?"

Package now also tracks:

- Its size (length, width, height) — needed to calculate shipping cost based on size, not just weight
- A scannable tracking code (similar to a barcode)
- Whether it contains hazardous materials, so it can be handled carefully

## Facility, Route, Vehicle & Driver

**Facility** now has a short code (like an airport code), a full address, GPS coordinates (latitude/longitude), and whether it's a certified secure facility.

**Route** now has a short code, an expected number of hours to complete the trip, and whether it's currently active or retired.

**Vehicle** now has an ID number (a VIN for trucks, or a tail number for planes), how much cargo space it has, and its current status (like "in service" or "under repair").

**Driver** now has an employee number, phone number, license expiration date, and current status.

---

# Naming Things and Choosing Data Types

## Better Naming

| Old Name | New Name |
|-----------|-------|
| sortation_lane | sorting_lane |

A small change, but plain English is easier to read than jargon.

## Using the Right Kind of Number

For money and measurements (like package dimensions), I used a data type called `NUMERIC` (also called `DECIMAL`) instead of `FLOAT`. Both store numbers, but `FLOAT` can sometimes round numbers slightly wrong — which is a real problem when you're dealing with money or exact measurements. `NUMERIC` keeps the numbers exact.

## Quote vs. Actual Payment

I kept two things separate on purpose:

- `quoted_amount` on the booking — the price estimate given to the customer up front
- `Payment.amount` — what was actually charged, which could happen more than once (the original charge, plus later extra charges for things like a heavier package or customs fees)

If I combined these into one number, I'd lose the ability to tell "what we told the customer it would cost" apart from "what we actually charged them."

## Timezones

Every timestamp that tracks something happening (like when a package arrived) uses a data type called `TIMESTAMPTZ`. Regular timestamps don't remember which timezone they were recorded in, which causes confusion for a company operating across the whole world. `TIMESTAMPTZ` keeps track of the timezone, so times are never mixed up.

---

# Only Keeping the Current Status

Columns like a vehicle's or driver's current status, or a booking/payment/shipment/leg's status, only store the **latest** value. When the status changes, the old value is simply overwritten and lost.

I thought about building a version that keeps a full history of every status change (so you could look back and see exactly when a shipment went from "in transit" to "delayed," for example). I decided not to build that yet — it would be a great feature to add later if I have more time, since it would help with tracking down problems.

---

# Rules I Didn't Add Yet

Right now, the database doesn't stop someone from typing in a random word for a status field. For example, `booking_status` should only ever be something like "pending," "confirmed," or "fulfilled" — but the database doesn't actually enforce that yet. I've written down the allowed values as documentation, but PostgreSQL itself isn't checking them.

Adding a rule that blocks bad values (called a `CHECK` constraint — a rule built into the database that rejects data that doesn't match a list of allowed values) is a good next step before this goes into real use.

---

# One Kind of Database, Not Two

This project is a **relational database** — a normal database made of connected tables, built to run a real system day-to-day (this is sometimes called "OLTP," short for a system that handles everyday transactions). It is **not** a "dimensional model," which is a different kind of database built specifically for big-picture reporting and analytics (using ideas like "facts" and "dimensions").

The rule I followed to keep the tables organized (called "3NF," or Third Normal Form — basically a checklist for avoiding repeated or badly organized data) is a relational-database idea. "Facts" and "dimensions" are a completely different, analytics-only idea, and they don't apply here.

One later feature — a "materialized view" (basically a saved, ready-made report that doesn't need to be recalculated every time) — is just a performance shortcut built on top of this same relational database. It doesn't mean the whole database changed into a different kind of system.

---

# What's Missing (On Purpose, For Now)

Things I chose not to build yet:

- `TrackingEvent` — a detailed log of every single scan (like every barcode or GPS ping). Right now, `PackageFacilityTransit` only tracks how long a package stayed at a warehouse, not every individual scan.
- GPS location pings
- RFID scans (a wireless tracking technology some warehouses use)
- Barcode scan events
- Filling the database with sample/test data — planned for later, using a tool called `Faker` that generates realistic fake data
- Rules that block bad status values (see [Rules I Didn't Add Yet](#rules-i-didnt-add-yet))
- Full history of status changes (see [Only Keeping the Current Status](#only-keeping-the-current-status))
- Convenience shortcuts in the code for navigating between connected tables (the database connections themselves are all there — this is just an extra layer that would make the code nicer to write)
- Extra indexes (an index is like the index at the back of a book — it helps the database find information faster). Right now only the ID columns are automatically indexed.
- Stored procedures (small pieces of code saved inside the database itself) — this was an optional bonus, not done yet
- Automated tests (code that automatically checks if everything still works correctly) — not done yet

These are all planned for a later phase of the project.

---

# Tools I Used

| Tool | Why I Chose It |
|------------|--------|
| PostgreSQL 18 | A free, powerful, and current database program |
| Docker | Lets me run the database in a self-contained "box" on my computer, so I don't have to install it directly — especially helpful since my laptop has limited disk space and runs two operating systems side by side |
| SQLAlchemy 2.0 | A tool that lets me write database tables using Python code instead of writing raw database commands by hand |
| Alembic | Keeps a history of every change I make to the database structure, so I can undo changes if something breaks |
| pydantic-settings | Safely loads settings (like passwords) from a separate file, so secret information never gets accidentally uploaded to a public code repository |
| Python Faker | A tool I plan to use later to generate realistic fake test data |

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
> Because I didn't know about this change at first, my database container kept failing to start — until I found and fixed the folder path.

---

# What's Next

## Planned for Later

- Keeping a full history of status changes, not just the current one
- Filling the database with realistic fake data using Faker
- Building views (saved queries) for reporting
- Building materialized views (saved, ready-made reports) for faster performance
- Adding indexes to speed up searches

---

<div align="center">

**Salome Gabriel**

</div>
