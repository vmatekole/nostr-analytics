# Decentralised Social Networks

A analytics/NLP engine for decentralised social networks.

## Problem statement
Data on Decentralised social networks is sharded and distributed across multiple nodes. Unlike blockchains there is no single source truth. Decentralised analytics aims to provide a robust, architecture that allows us for accurate analytics from decentralised networks such as Nostr and Farcaster.

## Supported Networks
- [Nostr](https://nostr.com/)
- [Farcaster] — TBD

## Tech Stack
- Python Engine
  - Data wrangling logic (Requesting prescribed [events](src/models/event.py) from relays)
  - Data pipelines/workflows implemented in Prefect
    - [Producer](src/models/kafka/producer.py) (retrieving events from [relays] via websockets)
    - [Consumer](src/models/kafka/consumer.py) (persisting events to BigQuery)
- Prefect for Orchestration
- Apache Kafka for data streaming
- BigQuery for Data Warehousing
- DBT for data modelling
- [MetaBase](https://www.metabase.com/) for dashboards
  - Overview dashboard
  - Number of active relays / users
  - Topics and subscriptions  <!-- Need to define thie better ->

## Deployment
- Single command deployment using Terraforma:
  - Data pipelines(Prefect application)
  - BigQuery datasets
  - Metabase dashboards

## Architecture

## Future considerations
– Splitting producer and consumer services


## Usage

## Acknowledgements
Thanks to [python-nostr] author of [python-nostr] where the Nostr [base models](src/models/nostr/) were largely taken from.
