 /*
  1. Write a query that aggregates the booking history per client. Filter for clients who have placed atleast  5 completed bookings and spent over a certain amount.
*/
 
 
-- Retrieving the average total spent by each client with confirmed booking and payment
select * from  payments_view;

with avg_client_totals as (

	select avg(t1.total_spent) as avg_spent	
 	from 
		(
	    select 
	    	c.client_id,
	    	sum(p.amount_in_naira) AS total_spent
	    from clients c
	    inner join shipment_bookings sb on c.client_id = sb.payer_client_id
	    inner join payments_view p on c.client_id = p.payer_client_id
	        and p.booking_id = sb.booking_id
	    where sb.booking_status = 'CONFIRMED'
	    group by c.client_id
		) as t1
)

-- Aggregating the booking history per client and filtering for customers who have placed atleast 
-- 5 completed bookings and spent over a the average total spent by each client.
select
    c."name" as clients_name,
    count(distinct sb.booking_id) as total_order,
    sum(p.amount_in_naira) as total_amount_spent
from clients c
inner join shipment_bookings sb on c.client_id = sb.payer_client_id
inner join payments_view p on c.client_id = p.payer_client_id
    and p.booking_id = sb.booking_id
where sb.booking_status = 'CONFIRMED'
group by c.client_id, c.name
having sum(p.amount_in_naira) > (select avg_spent from avg_client_totals)
and count(distinct sb.booking_id) > 5
order by total_amount_spent