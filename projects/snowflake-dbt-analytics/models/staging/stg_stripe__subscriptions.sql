-- stg_stripe__subscriptions.sql
-- Normalize Stripe subscription records and compute MRR/ARR per subscription.
-- Source: RAW.STRIPE.SUBSCRIPTIONS (loaded via Fivetran)

with source as (
    select * from {{ source('stripe', 'subscriptions') }}
),

renamed as (
    select
        id                                              as subscription_id,
        customer_id                                     as stripe_customer_id,
        lower(trim(status))                             as subscription_status, -- 'active','canceled','trialing','past_due'
        lower(trim(plan_id))                            as plan_id,
        lower(trim(plan_interval))                      as billing_interval,    -- 'month','year'
        plan_amount / 100.0                             as plan_amount_usd,     -- Stripe stores in cents

        -- Normalize to monthly MRR regardless of billing interval
        case
            when lower(trim(plan_interval)) = 'year'  then plan_amount / 100.0 / 12.0
            when lower(trim(plan_interval)) = 'month' then plan_amount / 100.0
            else 0
        end                                             as mrr_usd,

        -- ARR
        case
            when lower(trim(plan_interval)) = 'year'  then plan_amount / 100.0
            when lower(trim(plan_interval)) = 'month' then plan_amount / 100.0 * 12.0
            else 0
        end                                             as arr_usd,

        quantity,
        date(current_period_start)                      as period_start_date,
        date(current_period_end)                        as period_end_date,
        date(trial_start)                               as trial_start_date,
        date(trial_end)                                 as trial_end_date,
        date(canceled_at)                               as canceled_at_date,
        date(created)                                   as created_at_date,

        -- Churn flag
        case when lower(trim(status)) = 'canceled' then true else false end as is_churned,

        -- Trial flag
        case when lower(trim(status)) = 'trialing' then true else false end as is_trial,

        metadata_account_id                             as salesforce_account_id  -- custom metadata field

    from source
)

select * from renamed