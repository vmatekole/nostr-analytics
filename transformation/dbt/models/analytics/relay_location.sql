-- models/combined_location.sql

-- Create a new model that combines latitude and longitude into a single location column
-- You can adjust the schema and table name as needed

-- Replace `your_project` with your actual project name
{{ config(
  materialized='table',
  unique_key='url'
) }}

SELECT url, country_code, CONCAT(latitude, ',', longitude) AS location, inserted_at, policy.read, policy.write
FROM `nostr_production_data.relay`
