-- models/combined_location.sql

-- Create a new model that combines latitude and longitude into a single location column
-- You can adjust the schema and table name as needed

-- Replace `your_project` with your actual project name
{{ config(
  materialized='incremental'
) }}

SELECT content, pubkey, created_at, kind, sig, inserted_at
FROM`nostr_production_data.event`

{% if is_incremental() %}

  -- this filter will only be applied on an incremental run
  where inserted_at > (select max(inserted_at) from {{ this }})

{% endif %}
