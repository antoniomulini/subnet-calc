resource "google_pubsub_topic" "subnet_calc_topic" {
  name = "subnet-calc-topic"

  labels = {
    managedby = "terraform"
  }

  message_retention_duration = "86600s"
}

resource "google_pubsub_topic_iam_member" "subnet_calc_topic_iam" {
  project = var.gcp_project
  topic = google_pubsub_topic.subnet_calc_topic.id
  role = "roles/pubsub.publisher"
  member = "serviceAccount:chat-api-push@system.gserviceaccount.com"
}