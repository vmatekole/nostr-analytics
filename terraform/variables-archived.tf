################ PLEASE READ. THIS CODE IS ARCHIVED AND IS NO LONGER RELEVANT BUT GET FOR POSTERITY AND REFERENCE
variable "credentials" {
  description = "Terraform Credentials"
  default     =  "/Users/PI/code/datatalks/noble-velocity-411717-59617a8fb872-terraform.json"
  #ex: if you have a directory where this file is called keys with your service account json file
  #saved there as my-creds.json you could use default = "./keys/my-creds.json"
}

variable "gcp_key" {
    description = "gcp location"
    default = "GOOGLE_APPLICATION_CREDENTIALS"
}


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

variable "test_event_dataset_id" {
  description = "bq dataset id"
  default     = "test_event"
}

variable "test_event_table_id" {
  description = "bq table id"
  default     = "event"
}

variable "geolocation_dataset_id" {
  description = "bq table id"
  default     = "geolocation_data"

}

variable "geolocation_table_id" {
  description = "bq table id"
  default     = "ip_geolocation"
}
