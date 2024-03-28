variable "delete_protection" {
  default = false
}
provider "google" {
  project = var.project
  region  = var.region

}

resource "google_bigquery_dataset" "geolocation_data" {
  dataset_id                 = var.geolocation_dataset_id
  location                   = var.location
  delete_contents_on_destroy = true
}

resource "google_bigquery_table" "ip_geolocation" {
  dataset_id          = var.geolocation_dataset_id
  table_id            = var.geolocation_table_id
  depends_on          = [google_bigquery_dataset.geolocation_data]
  deletion_protection = false
  schema              = <<EOF
[
  {
    "name": "geoname_id",
    "type": "STRING",
    "mode": "REQUIRED"

  },
  {
    "name": "locale_code",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "continent_code",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "continent_name",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "country_iso_code",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "country_name",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "is_in_european_union",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "network",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "registered_country_geoname_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "represented_country_geoname_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "is_anonymous_proxy",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "is_satellite_provider",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "is_anycast",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "ip4_space",
    "type": "RECORD",
    "fields": [
      {
        "name": "network",
        "type": "STRING",
        "mode": "REQUIRED"
      },
      {
        "name": "registered_country_geoname_id",
        "type": "STRING",
        "mode": "REQUIRED"
      },
      {
        "name": "represented_country_geoname_id",
        "type": "STRING",
        "mode": "REQUIRED"
      },
      {
        "name": "is_anonymous_proxy",
        "type": "STRING",
        "mode": "REQUIRED"
      },
      {
        "name": "is_satellite_provider",
        "type": "STRING",
        "mode": "REQUIRED"
      },
      {
        "name": "is_anycast",
        "type": "STRING",
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
}
