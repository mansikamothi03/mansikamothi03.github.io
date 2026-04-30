-- ticket_volume_by_category.sql
-- Ticket volume, SLA breach rate, and avg resolution time by category.
-- Use this to identify which product areas drive the most support load.

select
    category,
    count(*)                                                        as total_tickets,
    round(count(*) * 100.0 / sum(count(*)) over (), 1)             as pct_of_total,

    -- SLA performance
    sum(case when is_sla_breached then 1 else 0 end)               as sla_breaches,
    round(
        sum(case when is_sla_breached then 1 else 0 end) * 100.0
        / nullif(count(*), 0), 1
    )                                                               as sla_breach_rate_pct,

    -- Resolution time
    round(avg(resolution_hours), 1)                                 as avg_resolution_hours,
    round(
        percentile_cont(0.5) within group (order by resolution_hours), 1
    )                                                               as median_resolution_hours,
    round(
        percentile_cont(0.95) within group (order by resolution_hours), 1
    )                                                               as p95_resolution_hours,

    -- CSAT
    count(case when csat_score = 'good' then 1 end)                as csat_good,
    count(case when csat_score = 'bad' then 1 end)                 as csat_bad,
    round(
        count(case when csat_score = 'good' then 1 end) * 100.0
        / nullif(count(case when csat_score is not null then 1 end), 0), 1
    )                                                               as csat_pct,

    -- Priority breakdown
    count(case when priority = 'urgent' then 1 end)                as urgent_tickets,
    count(case when priority = 'high' then 1 end)                  as high_tickets

from tickets
where created_at >= dateadd('day', -90, current_date)
group by category
order by total_tickets desc;