-- fct_support_load.sql
-- Weekly support load per account: ticket volume, SLA breaches, CSAT, resolution time.
-- Grain: one row per account per week.

with tickets as (
    select * from {{ ref('stg_zendesk__tickets') }}
),

accounts as (
    select * from {{ ref('stg_salesforce__accounts') }}
),

subscriptions as (
    select
        salesforce_account_id,
        sum(mrr_usd) as current_mrr,
        max(plan_id) as plan_id
    from {{ ref('stg_stripe__subscriptions') }}
    where subscription_status = 'active'
    group by 1
),

-- Map Zendesk organization_id to Salesforce account_id via accounts table
ticket_with_account as (
    select
        t.ticket_id,
        t.ticket_status,
        t.priority,
        t.ticket_type,
        t.channel,
        t.is_sla_breached,
        t.csat_score,
        t.resolution_hours,
        t.first_reply_hours,
        t.created_at_utc,
        t.solved_at_utc,
        date_trunc('week', t.created_at_utc)    as week_start,
        a.account_id                             as salesforce_account_id,
        a.account_name,
        a.account_type

    from tickets t
    left join accounts a on t.organization_id = a.account_id
),

weekly_support as (
    select
        salesforce_account_id,
        account_name,
        account_type,
        week_start,

        -- Volume
        count(ticket_id)                                                as total_tickets,
        count(case when priority = 'urgent' then 1 end)                 as p1_tickets,
        count(case when priority = 'high' then 1 end)                   as p2_tickets,

        -- SLA
        sum(case when is_sla_breached then 1 else 0 end)                as sla_breaches,
        round(
            sum(case when is_sla_breached then 1 else 0 end)::float
            / nullif(count(ticket_id), 0) * 100, 2
        )                                                               as sla_breach_rate_pct,

        -- Resolution time
        round(avg(resolution_hours), 1)                                 as avg_resolution_hours,
        round(avg(first_reply_hours), 1)                                as avg_first_reply_hours,
        round(percentile_cont(0.95) within group (
            order by resolution_hours
        ), 1)                                                           as p95_resolution_hours,

        -- CSAT
        count(case when csat_score = 'good' then 1 end)                 as csat_good,
        count(case when csat_score = 'bad' then 1 end)                  as csat_bad,
        round(
            count(case when csat_score = 'good' then 1 end)::float
            / nullif(count(case when csat_score is not null then 1 end), 0) * 100, 2
        )                                                               as csat_score_pct,

        -- Channel breakdown
        count(case when channel = 'email' then 1 end)                   as email_tickets,
        count(case when channel = 'chat' then 1 end)                    as chat_tickets,
        count(case when channel = 'web' then 1 end)                     as web_tickets

    from ticket_with_account
    group by 1, 2, 3, 4
)

select
    ws.*,
    s.current_mrr,
    s.plan_id,

    -- Support load score: weighted index (higher = more at-risk)
    round(
        (ws.p1_tickets * 3.0)
        + (ws.p2_tickets * 1.5)
        + (ws.sla_breach_rate_pct * 0.5)
        + (case when ws.csat_score_pct < 70 then 10 else 0 end)
    , 2)                                                                as support_load_score

from weekly_support ws
left join subscriptions s on ws.salesforce_account_id = s.salesforce_account_id
order by week_start desc, support_load_score desc