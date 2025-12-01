pipeline {
    agent any

    tools {
        nodejs "NodeJS" // Configure NodeJS tool in Jenkins
    }

    environment {
        REGISTRY = 'your-registry-url'
        IMAGE_NAME = 'devops-sample-app'
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/your-username/your-repo.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'npm install'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'npm test'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${env.IMAGE_NAME}:${env.BUILD_NUMBER}")
                }
            }
        }

        stage('Test Docker Image') {
            steps {
                script {
                    def image = docker.image("${env.IMAGE_NAME}:${env.BUILD_NUMBER}")
                    image.withRun("-p 3000:3000") { c ->
                        sh 'sleep 10' // Wait for container to start
                        sh 'curl -f http://localhost:3000/health || exit 1'
                    }
                }
            }
        }

        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry("https://${env.REGISTRY}", "dockerhub-credentials") {
                        def customImage = docker.image("${env.IMAGE_NAME}:${env.BUILD_NUMBER}")
                        customImage.push("latest")
                        customImage.push("${env.BUILD_NUMBER}")
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}