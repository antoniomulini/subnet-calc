# Deploys subnet calculator Google Chat bot as a Cloud Function in Python

provider "google" {
  credentials = file(var.gcp_creds_file)
  project     = var.gcp_project
  region      = var.gcp_region
}

data "archive_file" "zipit" {
  type        = "zip"
  source_file = "../python/main.py"
  output_path = "../python/subnetcalc.zip"
}

resource "google_storage_bucket" "bucket" {
  name     = "source-bucket-${var.gcp_project}-${var.gcp_region}"
  location = var.gcp_region
  project = var.gcp_project
}


resource "google_storage_bucket_object" "function_code" {
  name   = "subnetcalc.${data.archive_file.zipit.output_md5}.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.zipit.output_path
}

resource "google_cloudfunctions_function" "subnetcalc" {
  name        = "subnet-calc-bot"
  description = "Google Chat Bot for carrying out IP subnet calculations"
  runtime     = "python37"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.function_code.name
  trigger_http          = true
  entry_point           = "on_event"

  ingress_settings = "ALLOW_ALL"

}

resource "google_cloudfunctions_function_iam_binding" "binding" {
  project        = var.gcp_project
  region         = var.gcp_region
  cloud_function = google_cloudfunctions_function.subnetcalc.id
  role           = "roles/cloudfunctions.invoker"
  members        = [
    "allUsers"
  ]
}
