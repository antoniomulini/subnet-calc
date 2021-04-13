# Deploys subnet calculator Google Chat bot as a Cloud Function in Python

provider "google" {
  credentials = file(var.gcp_creds_file)
  project     = var.gcp_project
  region      = var.gcp_region
}


resource "google_storage_bucket" "bucket" {}


resource "google_storage_bucket_object" "archive" {}



resource "google_cloudfunctions_function" "function" {}




resource "google_cloudfunctions_function_iam_binding" "binding" {
  project = google_cloudfunctions_function.subnetcalc.project
  region = google_cloudfunctions_function.subnetcalc.region
  cloud_function = google_cloudfunctions_function.subnetcalc.name
  role = "roles/cloudfunctions.invoker"
  members = "allUsers"
}
