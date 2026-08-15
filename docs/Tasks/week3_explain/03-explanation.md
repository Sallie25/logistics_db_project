## Task 1 writeup
---

1. Before: Seq Scan on shipment_bookings with Rows Removed by Filter: 8000 — wasteful, reading all 10,000 rows to keep 2,000. Full query: 41.956 ms.
Created index on shipment_bookings.booking_status via Alembic migration.
Discovered the migration wasn't applied yet — alembic current showed the DB was one migration behind head. Ran alembic upgrade head to actually apply it — a good example of verifying assumptions rather than trusting that "generated" meant "applied."
---

2. After applying: isolated test confirmed the index works (Bitmap Index Scan, 3x faster on its own). Full query now naturally uses Bitmap Index Scan instead of Seq Scan — 41.956ms → 30.048ms, a ~28% improvement.
Honest caveat: the remaining cost in the full query comes from elsewhere 
---

3. (payments table still uses Seq Scan, the subquery duplicates the whole computation) — worth noting as a natural next optimization.
