/*
 2. Calculate the percentage of shipments delivered on time vs delayed per destination_city for orders shipped in the last 5 days
 */
select * from shipments;
select * from shipment_bookings;
select * from facilities;
select * from package_facility_transits;

select
    s.destination_facility_id,
    f.city,
    round(
        100.0 * count(case when actual_delivery_date <= estimated_delivery_date then 1 end) 
        / count(*), 2
    ) AS pct_on_time,
    round(
        100.0 * count(case when  actual_delivery_date > estimated_delivery_date THEN 1 end) 
        / count(*), 2
    ) AS pct_delayed
from shipments s
left join facilities f on s.destination_facility_id = f.facility_id 
where created_at >= current_date  - interval '5 days'
group by destination_facility_id,f.city;