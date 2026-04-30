-- assert_mrr_non_negative.sql
-- Custom dbt test: ensures no negative MRR values exist in fct_mrr.
-- A negative current_mrr (excluding churn rows) indicates a data pipeline error.

select
    account_id,
    month_start,
    current_mrr
from {{ ref('fct_mrr') }}
where current_mrr < 0
  and movement_type != 'churn'  -- churn rows legitimately have 0 MRR, not negative