-- Creating a view for payments that includes the conversion from dollar to naira.

create or replace view payments_view as
	select
		p.payment_id,
		p.payer_client_id,
		p.payment_type,
		p.payment_reference,
		p.payment_status,
		p.transaction_timestamp,
		p.booking_id,
		date_trunc('month', p.transaction_timestamp) as transaction_month,
    	p.amount as original_amount,
    	coalesce(r.rate_to_ngn, 1.00) as exchange_rate_used,
    	round(p.amount * coalesce(r.rate_to_ngn, 1.00), 2) as amount_in_naira
    from payments p
    left join exchange_rates r
    	on p.currency_code = r.currency_code;

    	