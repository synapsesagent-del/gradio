# Terraform configuration for deploying the application

terraform {
  required_version = ">= 1.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.22.0"
    }
  }
}

# Configure the Docker provider
provider "docker" {}

# Create a network for our application
resource "docker_network" "app_network" {
  name = "devops-sample-app-network"
}

# Run the application container
resource "docker_container" "app" {
  name  = "devops-sample-app"
  image = "nginx:latest"  # This would be replaced with your built image in a real scenario

  ports {
    internal = 80
    external = 3000
  }

  networks_advanced {
    name = docker_network.app_network.name
  }

  restart = "unless-stopped"
}

# Output the application URL
output "app_url" {
  value = "http://localhost:3000"
}