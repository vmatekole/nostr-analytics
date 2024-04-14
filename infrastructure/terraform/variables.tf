
############################ env VAR GOOGLE_APPLICATION_CREDENTIALS=/path/to/key/key.json has to be set to run this script ###########
variable "project" {
  description = "GCP Project"
  default     = "noble-velocity-411717"
}

variable "region" {
  description = "Region"
  #Update the below to your desired region
  default = "us-east1-b"
}

variable "location" {
  description = "Project Location"
  #Update the below to your desired location
  default = "US"
}

# Schemas Event & Relay

variable "event_schema" {
  default = <<EOF
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
    "name": "modified_at",
    "type": "TIMESTAMP",
    "mode": "NULLABLE"
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
        "mode": "REPEATED",
        "type": "STRING"
      }
    ]
  }
]
EOF

}

variable "relay_schema" {
  default = <<EOF
[
  {
    "name": "name",
    "type": "STRING"
  },
  {
    "name": "url",
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
    "name": "modified_at",
    "type": "TIMESTAMP",
    "mode": "NULLABLE"
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

}

# Test data variables
variable "test_event_dataset_id" {
  description = "bq dataset id"
  default     = "test_event"
}

variable "test_event_table_id" {
  description = "bq table id"
  default     = "event"
}

variable "test_relay_table_id" {
  description = "bq table id"
  default     = "relay"
}

# Production variables
variable "prd_nostr_dataset_id" {
  description = "bq dataset id"
  default     = "nostr_production_data"

}

variable "prd_event_table_id" {
  description = "bq table id"
  default     = "event"
}

variable "prd_relay_table_id" {
  description = "bq table id"
  default     = "relay"
}
