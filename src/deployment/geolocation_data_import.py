################ PLEASE READ. THIS CODE IS ARCHIVED AND IS NO LONGER RELEVANT BUT GET FOR POSTERITY AND REFERENCE
import csv
import sys
from typing import Any

from google.cloud import bigquery
from rich import print

from config import Settings


def import_data(
    dataset_id: str, table_id: str, ip4_csv_path: str, location_csv_path: str
):
    client = bigquery.Client()
    config = Settings()
    # dataset_ref: bigquery.DatasetReference = client.dataset(dataset_id)

    table_ref: bigquery.TableReference = bigquery.TableReference(
        bigquery.DatasetReference(config.gcp_project_id, dataset_id), table_id
    )
    # bigquery.Table(table_ref, BaseBQModel.bq_schema())
    table = client.get_table(table_ref)

    job_config = bigquery.LoadJobConfig()
    job_config.skip_leading_rows = 1
    job_config.source_format = bigquery.SourceFormat.CSV

    with open(location_csv_path, 'r') as location_file:
        location_data = list(csv.DictReader(location_file))

    with open(ip4_csv_path, 'r') as ip4_file:
        ip4_data = list(csv.DictReader(ip4_file))

    joined_data: list[Any] = []
    for location_row in location_data:
        joined_row = location_row.copy()
        for ip4_row in ip4_data:
            if location_row['geoname_id'] == ip4_row['registered_country_geoname_id']:
                if not 'ip4_space' in joined_row:
                    joined_row['ip4_space'] = []
                joined_row['ip4_space'].append(ip4_row)
        joined_data.append(joined_row)

    ROWS_SIZE: int = 1
    print(
        f'Importing {len(joined_data) / ROWS_SIZE} tranches of {ROWS_SIZE} rows to BigQuery '
    )
    for i in range(0, len(joined_data), ROWS_SIZE):
        chunk_of_rows: list[Any] = [joined_data[i]]
        try:
            errors = client.insert_rows_json(table, chunk_of_rows)
            if errors:
                raise Exception(f'Errors occurred while inserting rows: {errors}')
            else:
                print(f'{joined_data[i]["country_name"]} data added successfully')
        except Exception as e:
            print(
                f'Failed to add {joined_data[i]["country_name"]} Size(bytes): {sys.getsizeof(joined_data[i])}'
            )

    print(f'All {len(joined_data)} rows have been inserted successfully.')


if __name__ == '__main__':
    import_data(
        'geolocation_data', 'ip_geolocation', '../data/ip4.csv', '../data/location.csv'
    )
