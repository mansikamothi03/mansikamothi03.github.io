-- fct_mrr.sql
-- Monthly MRR movements per account: new, expansion, contraction, churn, reactivation.
-- Grain: one row per account per month.

with subscriptions as (
    select * from {{ ref('stg_stripe__subscriptions') }}
),

accounts as (
    select * from {{ ref('stg_salesforce__accounts') }}
),

-- Generate a spine of all months from start_date to today
month_spine as (
    select
        dateadd('month', seq4(), date_trunc('month', '{{ var("start_date") }}'::date)) as month_start
    from table(generator(rowcount => 60))  -- 5 years of months
    where month_start <= date_trunc('month', current_date())
),

-- Get MRR per subscription per month it was active
subscription_months as (
    select
        s.subscription_id,
        s.salesforce_account_id,
        s.plan_id,
        s.billing_interval,
        s.mrr_usd,
        s.is_churned,
        s.is_trial,
        m.month_start

    from subscriptions s
    join month_spine m
        on m.month_start >= date_trunc('month', s.created_at_date)
        and (
            s.canceled_at_date is null
            or m.month_start < date_trunc('month', s.canceled_at_date)
        )
    where s.is_trial = false  -- exclude trial MRR
),

-- Aggregate MRR per account per month
account_monthly_mrr as (
    select
        salesforce_account_id,
        month_start,
        sum(mrr_usd)    as mrr_usd,
        count(*)        as active_subscriptions
    from subscription_months
    group by 1, 2
),

-- Compute MRR movements using LAG
mrr_with_movements as (
    select
        a.salesforce_account_id,
        acc.account_name,
        acc.account_type,
        acc.industry,
        a.month_start,
        a.mrr_usd                                                   as current_mrr,
        coalesce(lag(a.mrr_usd) over (
            partition by a.salesforce_account_id
            order by a.month_start
        ), 0)                                                       as prior_mrr,
        a.active_subscriptions,

        -- MRR movement type
        case
            when coalesce(lag(a.mrr_usd) over (
                    partition by a.salesforce_account_id order by a.month_start), 0) = 0
                then 'new'
            when a.mrr_usd > coalesce(lag(a.mrr_usd) over (
                    partition by a.salesforce_account_id order by a.month_start), 0)
                then 'expansion'
            when a.mrr_usd < coalesce(lag(a.mrr_usd) over (
                    partition by a.salesforce_account_id order by a.month_start), 0)
                then 'contraction'
            else 'flat'
        end                                                         as movement_type,

        -- MRR delta
        a.mrr_usd - coalesce(lag(a.mrr_usd) over (
            partition by a.salesforce_account_id order by a.month_start
        ), 0)                                                       as mrr_delta

    from account_monthly_mrr a
    left join accounts acc on a.salesforce_account_id = acc.account_id
),

-- Add churn rows for accounts that had MRR last month but not this month
churned as (
    select
        prev.salesforce_account_id,
        acc.account_name,
        acc.account_type,
        acc.industry,
        dateadd('month', 1, prev.month_start)                       as month_start,
        0                                                           as current_mrr,
        prev.mrr_usd                                                as prior_mrr,
        0                                                           as active_subscriptions,
        'churn'                                                     as movement_type,
        -prev.mrr_usd                                               as mrr_delta

    from account_monthly_mrr prev
    left join account_monthly_mrr curr
        on prev.salesforce_account_id = curr.salesforce_account_id
        and curr.month_start = dateadd('month', 1, prev.month_start)
    left join accounts acc on prev.salesforce_account_id = acc.account_id
    where curr.salesforce_account_id is null
      and prev.mrr_usd > 0
      and dateadd('month', 1, prev.month_start) <= date_trunc('month', current_date())
)

select * from mrr_with_movements
union all
select * from churned
order by month_start, salesforce_account_id