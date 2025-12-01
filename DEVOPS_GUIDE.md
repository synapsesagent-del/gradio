# Complete DevOps Pipeline Guide

This document outlines a complete DevOps pipeline for a Node.js application with Docker, CI/CD, Infrastructure as Code, and Kubernetes deployment.

## Project Structure

```
/workspace/
├── README.md
├── package.json
├── server.js
├── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── infrastructure/
│   └── main.tf
├── kubernetes/
│   └── deployment.yaml
├── Jenkinsfile
├── Makefile
└── DEVOPS_GUIDE.md
```

## Components

### 1. Application Code
- **server.js**: Express.js application that responds with a simple JSON message
- **package.json**: Node.js dependencies and scripts

### 2. Containerization
- **Dockerfile**: Defines how to containerize the application
- **docker-compose.yml**: Local development environment configuration

### 3. CI/CD Pipeline
- **.github/workflows/ci-cd.yml**: GitHub Actions workflow for automated testing, building, and deployment
- **Jenkinsfile**: Alternative CI/CD pipeline for Jenkins

### 4. Infrastructure as Code
- **infrastructure/main.tf**: Terraform configuration to provision infrastructure

### 5. Container Orchestration
- **kubernetes/deployment.yaml**: Kubernetes deployment and service configuration

### 6. Automation
- **Makefile**: Simplified commands for common operations

## Getting Started

### Prerequisites
- Node.js 18+
- Docker
- Docker Compose
- Make (optional)

### Local Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the application**:
   ```bash
   npm start
   ```

3. **Or use Docker Compose**:
   ```bash
   docker-compose up --build
   ```

4. **Or use Make**:
   ```bash
   make install
   make start
   ```

### Docker Commands

```bash
# Build Docker image
make docker-build

# Run in Docker
make docker-run

# Stop Docker container
make docker-stop

# Clean up
make clean
```

### CI/CD Pipeline

The GitHub Actions workflow does the following:
1. Runs on push/PR to main/master branches
2. Tests the application
3. Builds and pushes Docker image to Docker Hub (when pushed to main)

### Kubernetes Deployment

To deploy to Kubernetes:

1. Update the image name in `kubernetes/deployment.yaml` with your Docker Hub image
2. Apply the configuration:
   ```bash
   kubectl apply -f kubernetes/deployment.yaml
   ```

### Infrastructure Deployment

To deploy infrastructure with Terraform:

1. Initialize:
   ```bash
   cd infrastructure
   terraform init
   ```

2. Plan and apply:
   ```bash
   terraform plan
   terraform apply
   ```

## Security Best Practices

1. **Secrets Management**: Store sensitive information (Docker Hub credentials, API keys) as secrets in your CI/CD platform
2. **Container Security**: Use minimal base images, scan images for vulnerabilities
3. **Infrastructure Security**: Use least-privilege IAM roles, enable encryption
4. **Code Security**: Keep dependencies updated, scan for vulnerabilities

## Monitoring and Logging

For a production environment, consider adding:
- Application performance monitoring (APM)
- Centralized logging (ELK stack, etc.)
- Infrastructure monitoring (Prometheus, Grafana)
- Health checks and alerts

## Scaling Considerations

- **Horizontal Pod Autoscaling**: Configure based on CPU/memory usage
- **Load Balancing**: Use cloud load balancers or ingress controllers
- **Database Scaling**: Separate database from application if needed
- **Caching**: Implement Redis or similar for caching

This setup provides a complete DevOps pipeline from development to production deployment with monitoring and security considerations.