class RelaySQL:
    @staticmethod
    def select_relays(dataset_id: str) -> str:
        return f'SELECT relay_name, relay_url, country_code, latitude, longitude, policy.read, policy.write FROM `{dataset_id}.relay`'
