terraform {
  required_version = ">= 1.0"
  
  required_providers {
    elasticstack = {
      source  = "elastic/elasticstack"
      version = "~>0.13"
    }

    ec = {
      source  = "elastic/ec"
      version = "~>0.13"
    }
  }
}

provider "ec" {
  apikey = var.elastic_cloud_api_key
}

data "ec_stack" "latest" {
  version_regex = "latest"
  region        = var.region
}

resource "ec_deployment" "demo_cluster" {
  region                 = var.region
  name                   = "demo_cluster"
  version                = data.ec_stack.latest.version
  deployment_template_id = var.deployment_template_id

  elasticsearch = {
    hot = {
      autoscaling = {}
      size = "8g"
      zone_count = 3
    }
  }
    
  kibana = {}
}

provider "elasticstack" {
  elasticsearch {
    endpoints = ["${ec_deployment.demo_cluster.elasticsearch.https_endpoint}"]
    username  = ec_deployment.demo_cluster.elasticsearch_username
    password  = ec_deployment.demo_cluster.elasticsearch_password
  }
  alias = "demo"
}
