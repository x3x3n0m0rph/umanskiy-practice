select 
	rides.passenger_count,
	avg(rides.tip_amount) as avg_tip,
	avg(rides.tip_amount) / GREATEST(rides.passenger_count, 1) as avg_tip_per_pass  -- zero passengers count means cargo-only ride
from rides
group by rides.passenger_count


select 
	date_trunc('month', rides.dropoff_datetime) as trip_month,
	avg(total_amount) avg_amount,
	sum(total_amount) total_earned
from rides
group by trip_month


select 
	rides.vendor_id as q,
	MAX(SQRT(POWER(p.x_0 - rides.pickup_longitude, 2) + POWER(p.y_0 - rides.pickup_latitude, 2))) as pickup_r,
	MAX(SQRT(POWER(p.y_0 - rides.pickup_latitude, 2) + POWER(p.y_1 - rides.dropoff_latitude, 2))) as dropoff_r
from rides
inner join (
	select vendor_id, 
		avg(pickup_longitude) as x_0, 
		avg(pickup_latitude) as y_0,
		avg(dropoff_longitude) as x_1, 
		avg(dropoff_latitude) as y_1
	from rides 
	where pickup_longitude != 0 
	  and pickup_latitude != 0 
	  and dropoff_longitude != 0
	  and dropoff_latitude != 0
	group by vendor_id
) as p on rides.vendor_id = p.vendor_id
where rides.pickup_longitude != 0 
	  and rides.pickup_latitude != 0 
	  and rides.dropoff_longitude != 0
	  and rides.dropoff_latitude != 0
group by vendor_id

# средняя скорость поездки 
select 
	t.*,
	(t.linear_dist_m / extract(epoch from elapsed_time)) as speed_mps
from ( select ctid, 
	(dropoff_datetime - pickup_datetime) as elapsed_time,
	st_point(pickup_longitude, pickup_latitude)::geography as pickup,
	st_point(dropoff_longitude, dropoff_latitude)::geography as dropoff,
	st_distance(
		st_point(pickup_longitude, pickup_latitude)::geography,
		st_point(dropoff_longitude, dropoff_latitude)::geography 
	) as linear_dist_m
	from rides
) as t
where 
		elapsed_time > INTERVAL '1 seconds'
	and elapsed_time < INTERVAL '1 days'
	and linear_dist_m > 0.0
	and linear_dist_m < 100000.0
order by speed_mps desc
limit 100;
