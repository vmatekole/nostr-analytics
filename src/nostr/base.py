from google.cloud import bigquery
from pydantic import BaseModel


class ModelBase(BaseModel):
    @classmethod
    def bq_schema(cls):
        type_mapping: dict[type[str] | type[int] | type[bool], str] = {
            str: 'STRING',
            int: 'INT64',
            bool: 'BOOL',
        }

        schema: List[bigquery.SchemaField] = [
            bigquery.SchemaField(
                name,
                type_mapping.get(field.annotation, 'STRING'),
                mode=cls._get_field_mode(name, field),
            )
            for name, field in cls.model_fields.items()
            if not name == 'tags'
        ]
        schema.append(
            bigquery.SchemaField(
                'tags',
                'RECORD',
                'REPEATED',
                None,
                None,
                (
                    bigquery.SchemaField(
                        'tag', 'STRING', 'REPEATED', None, None, (), None
                    ),
                ),
                None,
            ),
        )

        return schema
