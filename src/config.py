from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')
    priv_key: str
    pub_key: str
    kafka_url: str
    kafka_user: str
    kafka_pass: str
    kafka_schema_url: str
    kafka_schema_auth_token: str
    kafka_consumer_group: str
    gcp_project_id: str
    test_event_bq_table_id: str
    test_event_bq_dataset_id: str
    ip_geolocation_url: str
    ip_geolocation_key: str
