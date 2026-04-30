-- stg_salesforce__accounts.sql
-- Normalize and deduplicate raw Salesforce account records.
-- Source: RAW.SALESFORCE.ACCOUNTS (loaded via Fivetran)

with source as (
    select * from {{ source('salesforce', 'accounts') }}
),

renamed as (
    select
        id                                          as account_id,
        name                                        as account_name,
        lower(trim(type))                           as account_type,       -- 'customer', 'prospect', 'partner'
        lower(trim(industry))                       as industry,
        lower(trim(billing_country))                as billing_country,
        annual_revenue                              as annual_revenue_usd,
        number_of_employees                         as employee_count,
        lower(trim(owner_id))                       as owner_id,
        lower(trim(account_source))                 as acquisition_source,
        date(created_date)                          as created_at,
        date(last_modified_date)                    as updated_at,
        is_deleted

    from source
    where is_deleted = false
),

deduped as (
    select *,
        row_number() over (
            partition by account_id
            order by updated_at desc
        ) as row_num
    from renamed
)

select * from deduped
where row_num = 1