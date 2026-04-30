-- agent_performance.sql
-- Agent-level performance metrics: volume handled, resolution time, CSAT, SLA compliance.
-- Use this to identify top performers and coaching opportunities.

select
    agent,
    count(*)                                                        as tickets_handled,

    -- Resolution time
    round(avg(resolution_hours), 1)                                 as avg_resolution_hours,
    round(
        percentile_cont(0.5) within group (order by resolution_hours), 1
    )                                                               as median_resolution_hours,

    -- First reply time
    round(avg(first_reply_hours), 1)                                as avg_first_reply_hours,

    -- SLA compliance
    sum(case when is_sla_breached then 1 else 0 end)               as sla_breaches,
    round(
        (1 - sum(case when is_sla_breached then 1 else 0 end) * 1.0
        / nullif(count(*), 0)) * 100, 1
    )                                                               as sla_compliance_pct,

    -- CSAT
    count(case when csat_score = 'good' then 1 end)                as csat_good,
    count(case when csat_score = 'bad' then 1 end)                 as csat_bad,
    round(
        count(case when csat_score = 'good' then 1 end) * 100.0
        / nullif(count(case when csat_score is not null then 1 end), 0), 1
    )                                                               as csat_pct,

    -- Priority mix (higher % urgent = harder workload)
    round(
        count(case when priority = 'urgent' then 1 end) * 100.0
        / nullif(count(*), 0), 1
    )                                                               as pct_urgent,

    -- Category specialization (most common category for this agent)
    mode() within group (order by category)                        as top_category

from tickets
where status in ('solved', 'closed')
  and created_at >= dateadd('day', -90, current_date)
group by agent
having count(*) >= 10  -- exclude agents with very few tickets
order by csat_pct desc, sla_compliance_pct desc;