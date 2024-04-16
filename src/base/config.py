import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding='utf-8')
    priv_key: str
    pub_key: str
    kafka_url: str
    kafka_user: str
    kafka_pass: str
    kafka_schema_url: str
    kafka_schema_auth_token: str
    kafka_consumer_group: str
    gcp_project_id: str
    bq_dataset_id: str
    bq_event_table_id: str
    bq_relay_table_id: str
    ip_geolocation_url: str
    ip_geolocation_key: str
    relay_refresh_ip_geo_relay_info: bool
    max_connected_relays: int
    test_without_internet: bool
    relay_kafka_topic: str
    event_kafka_topic: str


ConfigSettings = Settings(_env_file=os.environ['NOSTR_A_ENV'])
