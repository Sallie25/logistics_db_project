/*4 calculate the Month-over-Month Revenue growth rate*/

with previous_month_earnings as (
	select 
		transaction_month,
		sum(amount_in_naira) as current_month_earnings_in_naira,
		lag(sum(amount_in_naira),1,0) over w as previous_month_earnings_in_naira
	from payments_view
	group by transaction_month
	window w as (order by transaction_month)
	
)
 
select 
	*,
	(current_month_earnings_in_naira - previous_month_earnings_in_naira)  as mom_change,
	round(((current_month_earnings_in_naira - previous_month_earnings_in_naira) / nullif(previous_month_earnings_in_naira, 0)) * 100,2) as mom_rev_growth_rate 
from previous_month_earnings