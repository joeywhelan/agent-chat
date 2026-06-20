output "elasticsearch_url" {
  value = ec_deployment.demo_cluster.elasticsearch.https_endpoint
}

output "elasticsearch_username" {
  value = ec_deployment.demo_cluster.elasticsearch_username
}

output "elasticsearch_password" {
  value     = ec_deployment.demo_cluster.elasticsearch_password
  sensitive = true
}