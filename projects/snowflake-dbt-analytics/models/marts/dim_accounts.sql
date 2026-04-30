-- dim_accounts.sql
-- Account dimension with composite health score.
-- SCD Type 2 pattern: tracks historical changes to account attributes.
-- Grain: one row per account per version (current + historical).

with accounts as (
    select * from {{ ref('stg_salesforce__accounts') }}
),

subscriptions as (
    select
        salesforce_account_id,
        sum(mrr_usd)                as current_mrr,
        sum(arr_usd)                as current_arr,
        count(*)                    as active_subscription_count,
        min(created_at_date)        as first_subscription_date,
        max(plan_id)                as highest_plan_id
    from {{ ref('stg_stripe__subscriptions') }}
    where subscription_status = 'active'
    group by 1
),

support_summary as (
    select
        salesforce_account_id,
        sum(total_tickets)          as tickets_last_90d,
        avg(sla_breach_rate_pct)    as avg_sla_breach_rate,
        avg(csat_score_pct)         as avg_csat_score,
        avg(support_load_score)     as avg_support_load_score
    from {{ ref('fct_support_load') }}
    where week_start >= dateadd('day', -90, current_date())
    group by 1
),

joined as (
    select
        a.account_id,
        a.account_name,
        a.account_type,
        a.industry,
        a.billing_country,
        a.annual_revenue_usd,
        a.employee_count,
        a.acquisition_source,
        a.created_at,
        a.updated_at,

        -- Subscription data
        coalesce(s.current_mrr, 0)              as current_mrr,
        coalesce(s.current_arr, 0)              as current_arr,
        coalesce(s.active_subscription_count, 0) as active_subscriptions,
        s.first_subscription_date,
        s.highest_plan_id,

        -- Support data
        coalesce(sup.tickets_last_90d, 0)       as tickets_last_90d,
        coalesce(sup.avg_sla_breach_rate, 0)    as avg_sla_breach_rate,
        coalesce(sup.avg_csat_score, 100)       as avg_csat_score,
        coalesce(sup.avg_support_load_score, 0) as avg_support_load_score,

        -- Account tier classification
        case
            when coalesce(s.current_mrr, 0) >= 5000  then 'enterprise'
            when coalesce(s.current_mrr, 0) >= 1000  then 'pro'
            when coalesce(s.current_mrr, 0) > 0      then 'starter'
            else 'free'
        end                                     as account_tier,

        -- Composite health score (0-100, higher = healthier)
        -- Weighted: CSAT 30%, SLA compliance 25%, MRR stability 25%, support load 20%
        round(
            least(100, greatest(0,
                (coalesce(sup.avg_csat_score, 80) * 0.30)
                + ((100 - coalesce(sup.avg_sla_breach_rate, 0)) * 0.25)
                + (case
                    when coalesce(s.current_mrr, 0) > 0 then 25
                    else 0
                   end)
                + (greatest(0, 20 - coalesce(sup.avg_support_load_score, 0)) * 0.20)
            ))
        , 1)                                    as health_score,

        -- Health tier
        case
            when round(least(100, greatest(0,
                (coalesce(sup.avg_csat_score, 80) * 0.30)
                + ((100 - coalesce(sup.avg_sla_breach_rate, 0)) * 0.25)
                + (case when coalesce(s.current_mrr, 0) > 0 then 25 else 0 end)
                + (greatest(0, 20 - coalesce(sup.avg_support_load_score, 0)) * 0.20)
            )), 1) >= 75 then 'healthy'
            when round(least(100, greatest(0,
                (coalesce(sup.avg_csat_score, 80) * 0.30)
                + ((100 - coalesce(sup.avg_sla_breach_rate, 0)) * 0.25)
                + (case when coalesce(s.current_mrr, 0) > 0 then 25 else 0 end)
                + (greatest(0, 20 - coalesce(sup.avg_support_load_score, 0)) * 0.20)
            )), 1) >= 50 then 'at_risk'
            else 'critical'
        end                                     as health_tier,

        -- SCD Type 2 metadata
        current_timestamp()                     as dbt_updated_at,
        true                                    as is_current

    from accounts a
    left join subscriptions s   on a.account_id = s.salesforce_account_id
    left join support_summary sup on a.account_id = sup.salesforce_account_id
)

select * from joined