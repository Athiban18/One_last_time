pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'cheenu181'                    // DockerHub username
        DOCKERHUB_PASS = credentials('dockerhub-token') // Jenkins credential ID
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out code from GitHub..."
                git branch: 'main', url: 'https://github.com/Athiban18/One_last_time.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "Building frontend Docker image..."
                sh 'docker build -t $DOCKERHUB_USER/akfinity-frontend:latest ./frontend'
                echo "Building backend Docker image..."
                sh 'docker build -t $DOCKERHUB_USER/akfinity-backend:latest ./backend'
            }
        }

        stage('Push Docker Images') {
            steps {
                echo "Logging in to DockerHub..."
                sh 'echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin'
                echo "Pushing frontend image..."
                sh 'docker push $DOCKERHUB_USER/akfinity-frontend:latest'
                echo "Pushing backend image..."
                sh 'docker push $DOCKERHUB_USER/akfinity-backend:latest'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! ✅'
        }
        failure {
            echo 'Pipeline failed ❌ Check the logs.'
        }
    }
}

