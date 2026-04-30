-- stg_zendesk__tickets.sql
-- Normalize Zendesk ticket events and compute SLA breach flags.
-- Source: RAW.ZENDESK.TICKETS (loaded via Fivetran)

with source as (
    select * from {{ source('zendesk', 'tickets') }}
),

renamed as (
    select
        id                                              as ticket_id,
        lower(trim(status))                             as ticket_status,       -- 'new','open','pending','solved','closed'
        lower(trim(priority))                           as priority,            -- 'low','normal','high','urgent'
        lower(trim(type))                               as ticket_type,         -- 'question','incident','problem','task'
        subject                                         as ticket_subject,
        lower(trim(channel))                            as channel,             -- 'email','web','api','chat'
        requester_id                                    as requester_id,
        assignee_id                                     as assignee_id,
        organization_id                                 as organization_id,
        group_id                                        as group_id,
        convert_timezone('UTC', created_at)             as created_at_utc,
        convert_timezone('UTC', updated_at)             as updated_at_utc,
        convert_timezone('UTC', solved_at)              as solved_at_utc,
        convert_timezone('UTC', first_reply_at)         as first_reply_at_utc,

        -- Resolution time in hours
        datediff(
            'hour',
            convert_timezone('UTC', created_at),
            convert_timezone('UTC', solved_at)
        )                                               as resolution_hours,

        -- First reply time in hours
        datediff(
            'hour',
            convert_timezone('UTC', created_at),
            convert_timezone('UTC', first_reply_at)
        )                                               as first_reply_hours,

        -- SLA breach flag: P1/urgent > 4h first reply, P2/high > 8h, others > 24h
        case
            when lower(trim(priority)) = 'urgent' and datediff('hour', created_at, first_reply_at) > 4  then true
            when lower(trim(priority)) = 'high'   and datediff('hour', created_at, first_reply_at) > 8  then true
            when lower(trim(priority)) in ('normal','low') and datediff('hour', created_at, first_reply_at) > 24 then true
            else false
        end                                             as is_sla_breached,

        satisfaction_rating_score                       as csat_score,         -- 'good','bad',null
        tags                                            as tags_array,
        is_public

    from source
)

select * from renamed