variable "delete_protection" {
  default = false
}
provider "google" {
  project = var.project
  region  = var.region

}

resource "google_bigquery_dataset" "nostr_production_data" {
  dataset_id                 = var.prd_nostr_dataset_id
  location                   = var.location
  delete_contents_on_destroy = true
}


resource "google_bigquery_dataset" "test_events" {
  dataset_id = var.test_event_dataset_id
}

resource "google_bigquery_table" "event" {
  dataset_id          = google_bigquery_dataset.test_events.dataset_id
  depends_on          = [google_bigquery_dataset.test_events]
  table_id            = "event"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "content",
    "type": "STRING"
  },
  {
    "name": "pubkey",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "created_at",
    "type": "INT64",
    "mode": "REQUIRED"
  },
  {
    "name": "inserted_at",
    "type": "TIMESTAMP",
    "mode": "NULLABLE",
    "description": "DEFAULT CURRENT_TIMESTAMP()"
  },
  {
    "name": "kind",
    "type": "INT64",
    "mode": "REQUIRED"
  },
  {
    "name": "sig",
    "type": "STRING"
  },
  {
    "name": "tags",
    "type": "RECORD",
    "mode": "REPEATED",
    "fields": [
      {
        "name": "tag_id",
        "type": "INT64"
      },
      {
        "name": "tag_values",
        "type": "RECORD",
        "mode": "REPEATED",
        "fields": [
          {
            "name": "tag_value",
            "type": "STRING"
          }
        ]
      }
    ]
  }
]
EOF
}


resource "google_bigquery_table" "relay" {
  dataset_id          = var.prd_nostr_dataset_id
  table_id            = var.prd_relay_table_id
  depends_on          = [google_bigquery_dataset.nostr_production_data]
  deletion_protection = true
  schema              = <<EOF
[
  {
    "name": "relay_name",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "relay_url",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "country_code",
    "type": "STRING"
  },
  {
    "name": "latitude",
    "type": "FLOAT64"
  },
  {
    "name": "longitude",
    "type": "FLOAT64"
  },
  {
    "name": "inserted_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "policy",
    "type": "RECORD",
    "fields": [
      {
        "name": "read",
        "type": "BOOLEAN",
        "mode": "REQUIRED"
      },
      {
        "name": "write",
        "type": "BOOLEAN",
        "mode": "REQUIRED"
      }
    ]
  }
]
EOF

  #   provisioner "local-exec" {
  #     command     = "python import_data.py"
  #     working_dir = path.module
  #   }
  lifecycle {
    prevent_destroy = false
  }

  #  This is a workaround not being able to set default values with terraform when creating the schema
  provisioner "local-exec" {
    command = "bq query --use_legacy_sql=false 'ALTER TABLE ${var.prd_nostr_dataset_id}.${var.prd_relay_table_id} ALTER COLUMN inserted_at SET DEFAULT CURRENT_TIMESTAMP()'"
  }
}
