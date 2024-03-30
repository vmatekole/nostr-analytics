
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
