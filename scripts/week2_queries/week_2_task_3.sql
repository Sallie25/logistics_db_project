/* 3. Define a MATERIALIZED VIEW named mv_customer_monthly_spend_summary that aggregates monthly spend by customer for fast querying by BI tools. 
 
 Write the refresh command as a comment below the view script.*/

-- drop materialized view mv_client_monthly_spend_summary before creating it
drop materialized view mv_client_monthly_spend_summary;

-- create materialized view mv_client_monthly_spend_summary
create materialized view mv_client_monthly_spend_summary as
select 
	c.client_id,
	c.name,
	p.transaction_month,
	to_char(p.transaction_month, 'Month') AS month_name,
	sum(p.amount_in_naira) AS total_spent
from clients c
inner join shipment_bookings sb on c.client_id = sb.payer_client_id
inner join payments_view p on c.client_id = p.payer_client_id
    and p.booking_id = sb.booking_id
group by c.client_id, c.name, p.transaction_month,to_char(p.transaction_month, 'Month');

-- refresh materialized view mv_client_monthly_spend_summary
refresh materialized view mv_client_monthly_spend_summary;
