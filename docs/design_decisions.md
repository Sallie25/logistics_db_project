#  Design Decisions — DHL-Style Logistics Database

<div align="center">

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Normalization](https://img.shields.io/badge/Normalization-3NF-success)
![Status](https://img.shields.io/badge/Project-Week%201-blue)
![License](https://img.shields.io/badge/License-MIT-green)

*A normalized PostgreSQL logistics database inspired by DHL-style carrier operations.*

</div>

---

# 📑 Table of Contents

- [Overview](#overview)
- [Project Goals](#project-goals)
- [Domain Model Decision](#domain-model-decision)
- [Entity Overview](#entity-overview)
- [ER Diagram](#er-diagram)
- [Relationship Decisions](#relationship-decisions)
    - Client → ShipmentBooking
    - ShipmentBooking → Shipment
    - ShipmentBooking → Payment
    - Shipment ↔ Vehicle / Driver
    - Package ↔ Facility
    - Route → Facility
- [Role-Based Foreign Keys](#role-based-foreign-keys)
- [Naming & Data Types](#naming--data-types)
- [Known Limitations](#known-limitations)
- [Technology Choices](#technology-choices)
- [Docker Troubleshooting](#docker-troubleshooting)
- [Future Improvements](#future-improvements)
- [Lessons Learned](#lessons-learned)

---

# Overview

> This document explains **why** each design decision was made—not merely *what* the schema looks like.
>
> Every table, relationship, foreign key, and data type exists because it models a real logistics operation while remaining fully normalized.

---

# Project Goals

The objective of this project was to design a PostgreSQL database capable of representing a modern carrier network similar to DHL, FedEx, or UPS.

The emphasis was on:

- ✅ Normalization
- ✅ Referential Integrity
- ✅ Real-world business rules
- ✅ Extensibility
- ✅ PostgreSQL best practices

---

# Domain Model Decision

## Why not an E-Commerce Schema?

Initially, I evaluated several Kaggle e-commerce datasets.

Those datasets revolve around:

- Products
- Sellers
- Orders
- Shopping carts
- Discounts
- Reviews

Which wasn't what i was going for.

A carrier database has completely different priorities.

```
Customer
    │
Books Shipment
    │
Shipment
    │
Transport Network
    │
Facilities
    │
Vehicles
    │
Recipient
```

Instead of asking

> "What product did the customer buy?"

the database asks

> "Where is this package?"

That single difference completely changes the schema.

---

# Entity Overview

| Entity | Responsibility |
|----------|----------------|
| Client | People or organizations involved in shipments |
| ShipmentBooking | Customer shipping request |
| Shipment | Physical movement |
| Package | Individual parcels |
| Facility | Warehouses & hubs |
| Route | Planned transportation path |
| TransportLeg | Individual journey segment |
| Vehicle | Trucks, vans, aircraft |
| Driver | Vehicle operators |
| Payment | Booking payment |
| PackageFacilityTransit | Package movement through facilities |

---

# ER Diagram

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
              │1             │1
              │              │
             N│             1│
              ▼              ▼
      +-------------+    +---------+
      | Shipment    |    | Payment |
      +-------------+    +---------+
            │
            │1
            │
           N│
            ▼
      +-------------+
      | Package     |
      +-------------+
            │
            │
            │ N
            │
            ▼
+--------------------------+
| PackageFacilityTransit   |
+--------------------------+
            ▲
            │
            │N
            │
            ▼
      +-------------+
      | Facility    |
      +-------------+

Shipment
     │
     │N
     ▼
TransportLeg
     ▲
     │
 Vehicle / Driver
```

---

# Relationship Decisions

## 1️⃣ Client → ShipmentBooking

*** Note
> One client can appear three different times inside the same booking.

```
Client
   │
   ├── sender_client_id
   ├── receiver_client_id
   └── payer_client_id
```

These are **roles**, not different entity types.

Having separate Sender, Receiver, and Payer tables would massively duplicate data.

---

## 2️⃣ ShipmentBooking → Shipment

```
Booking
   │
   ├── Shipment (Abuja)
   ├── Shipment (Kano)
   └── Shipment (Port Harcourt)
```

One booking may produce several physical shipments.

This is common in enterprise logistics.

---

## 3️⃣ ShipmentBooking → Payment

Current implementation:

```
Booking
   │
   ▼
Payment
```

1:1 relationship.

*** Note
> Production systems usually require:
>
> - Split payments
> - Refunds
> - Multiple currencies
> - Partial payments

---

## 4️⃣ Shipment ↔ Vehicle

Instead of

```
Shipment
    vehicle_id
```

(which breaks immediately)

we model

```
Shipment
      │
      ▼
 TransportLeg
      ▲
      │
Vehicle
```

because shipments switch vehicles throughout their journey.

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

This associative entity stores:

- inbound_timestamp
- outbound_timestamp
- sorting_lane

Those attributes belong to the relationship—not either entity individually.

---

## 6️⃣ Route → Facility

```
Facility
     ▲
     │ origin
 Route
     │ destination
     ▼
Facility
```

Exactly the same role-based FK pattern used by Client.

---

# Role-Based Foreign Keys

> [!TIP]
> One entity.
>
> Multiple contextual roles.

A Client can be:

- Sender today
- Receiver tomorrow
- Payer next week

Still the same Client.

This avoids duplicate tables while preserving business meaning.

---

# Naming & Data Types

## Better Naming

| Original | Final |
|-----------|-------|
| sortation_lane | sorting_lane |

Small change.

Much more readable.

---


## Timezones

Every tracking timestamp uses

```sql
TIMESTAMPTZ
```

because logistics doesn't stop at one timezone.

---

# Known Limitations


Current project intentionally excludes:

- TrackingEvent
- GPS pings
- RFID scans
- Barcode events
- Python data seeding

These are planned for Phase 2.

---

# Technology Choices

| Technology | Reason |
|------------|--------|
| PostgreSQL 18 | Latest stable release |
| Docker | Reproducible environment |
| SQL | Relational modeling |
| Python Faker | Planned data generation |

---

# Docker Troubleshooting

## PostgreSQL 18 Volume Mount

Older tutorials recommend

```yaml
/var/lib/postgresql/data
```

PostgreSQL 18 required

```yaml
/var/lib/postgresql
```

because of changes related to **pg_ctlcluster**.

> [!CAUTION]
> This version-specific difference caused startup failures until the mount path was corrected.

---

# Future Improvements

## Phase 2

- Shipment status history (SCD 2)
- Faker-powered seeding
- Analytics views
- Materialized views
- Index optimization

---



<div align="center">

**Salome Gabriel**

</div>
