provider "google" {
  project = var.project
  region  = var.region

}

resource "google_bigquery_dataset" "test_events" {
  dataset_id = var.test_event_dataset_id
}

resource "google_bigquery_table" "test_event" {
  dataset_id          = google_bigquery_dataset.test_events.dataset_id
  table_id            = var.test_event_table_id
  depends_on          = [google_bigquery_dataset.test_events]
  deletion_protection = false
  schema              = var.event_schema
}

resource "google_bigquery_table" "test_relay" {
  dataset_id          = var.test_event_dataset_id
  table_id            = var.test_relay_table_id
  depends_on          = [google_bigquery_dataset.test_events]
  deletion_protection = false
  schema              = var.relay_schema

  #   provisioner "local-exec" {
  #     command     = "python import_data.py"
  #     working_dir = path.module
  #   }
  lifecycle {
    prevent_destroy = false
  }

  # TODO: Need to refactor into a loop

  #  This is a workaround not being able to set default values with terraform when creating the schema
  provisioner "local-exec" {
    command = "bq query --use_legacy_sql=false 'ALTER TABLE ${var.test_event_dataset_id}.${var.test_event_table_id} ALTER COLUMN inserted_at SET DEFAULT CURRENT_TIMESTAMP()'"
  }

  provisioner "local-exec" {
    command = "bq query --use_legacy_sql=false 'ALTER TABLE ${var.test_event_dataset_id}.${var.test_relay_table_id} ALTER COLUMN inserted_at SET DEFAULT CURRENT_TIMESTAMP()'"
  }
}

# #################### PRODUCTION SCHEMAS #####################

resource "google_bigquery_dataset" "nostr_production_data" {
  dataset_id                 = var.prd_nostr_dataset_id
  location                   = var.location
  delete_contents_on_destroy = true
}

resource "google_bigquery_table" "prd_event" {
  dataset_id          = var.prd_nostr_dataset_id
  table_id            = var.prd_event_table_id
  depends_on          = [google_bigquery_dataset.nostr_production_data]
  deletion_protection = false
  schema = var.event_schema
}


resource "google_bigquery_table" "prd_relay" {
  dataset_id          = var.prd_nostr_dataset_id
  table_id            = var.prd_relay_table_id
  depends_on          = [google_bigquery_dataset.nostr_production_data]
  deletion_protection = true
  schema              = var.relay_schema

  #   provisioner "local-exec" {
  #     command     = "python import_data.py"
  #     working_dir = path.module
  #   }
  lifecycle {
    prevent_destroy = false
  }

  # TODO: Need to refactor into a loop
  # This is a workaround not being able to set default values with terraform when creating the schema
  provisioner "local-exec" {
    command = "bq query --use_legacy_sql=false 'ALTER TABLE ${var.prd_nostr_dataset_id}.${var.prd_event_table_id} ALTER COLUMN inserted_at SET DEFAULT CURRENT_TIMESTAMP()'"
  }

  provisioner "local-exec" {
    command = "bq query --use_legacy_sql=false 'ALTER TABLE ${var.prd_nostr_dataset_id}.${var.prd_relay_table_id} ALTER COLUMN inserted_at SET DEFAULT CURRENT_TIMESTAMP()'"
  }
}
