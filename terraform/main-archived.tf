################ PLEASE READ. THIS CODE IS ARCHIVED AND IS NO LONGER RELEVANT BUT GET FOR POSTERITY AND REFERENCE

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
    "type": "STRING"

  },
  {
    "name": "locale_code",
    "type": "STRING"
  },
  {
    "name": "continent_code",
    "type": "STRING"
  },
  {
    "name": "continent_name",
    "type": "STRING"
  },
  {
    "name": "country_iso_code",
    "type": "STRING"
  },
  {
    "name": "country_name",
    "type": "STRING"
  },
  {
    "name": "is_in_european_union",
    "type": "STRING"
  },
  {
    "name": "network",
    "type": "STRING"
  },
  {
    "name": "registered_country_geoname_id",
    "type": "STRING"
  },
  {
    "name": "represented_country_geoname_id",
    "type": "STRING"
  },
  {
    "name": "is_anonymous_proxy",
    "type": "STRING"
  },
  {
    "name": "is_satellite_provider",
    "type": "STRING"
  },
  {
    "name": "is_anycast",
    "type": "STRING"
  },
  {
    "name": "ip4_space",
    "type": "RECORD",
    "mode": "REPEATED",
    "fields": [
      {
        "name": "network",
        "type": "STRING"
      },
      {
        "name": "geoname_id",
        "type": "STRING"
      },
      {
        "name": "registered_country_geoname_id",
        "type": "STRING"
      },
      {
        "name": "represented_country_geoname_id",
        "type": "STRING"
      },
      {
        "name": "is_anonymous_proxy",
        "type": "STRING"
      },
      {
        "name": "is_satellite_provider",
        "type": "STRING"
      },
      {
        "name": "is_anycast",
        "type": "STRING"
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
