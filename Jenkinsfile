pipeline {
    agent any
    environment {
        DOCKERHUB_USER = 'cheenu181'             // Your DockerHub username
        DOCKERHUB_PASS = credentials('dockerhub-token')  // ID of Jenkins credential
    }
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/Athiban18/One_last_time.git'
            }
        }
        stage('Build Docker Images') {
            steps {
                sh 'docker build -t $DOCKERHUB_USER/akfinity-frontend:latest ./frontend'
                sh 'docker build -t $DOCKERHUB_USER/akfinity-backend:latest ./backend'
            }
        }
        stage('Push Docker Images') {
            steps {
                sh 'echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin'
                sh 'docker push $DOCKERHUB_USER/akfinity-frontend:latest'
                sh 'docker push $DOCKERHUB_USER/akfinity-backend:latest'
            }
        }
    }
}

