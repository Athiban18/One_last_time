pipeline {
    agent any

    environment {
        // Configure these in Jenkins Credentials and Global Env
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_NAMESPACE   = "cheenu181"   // change if different
        APP_NAME              = "one_last_time"
        IMAGE_TAG             = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    triggers {
        // Build when GitHub push happens (use GitHub plugin / webhook)
        pollSCM('')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Python (lint/test)') {
            steps {
                sh 'python --version || true'
                sh 'pip --version || true'
            }
        }

        stage('Install deps (optional)') {
            steps {
                sh 'python -m pip install --upgrade pip || true'
                sh 'pip install -r one_last_time/requirements.txt || true'
            }
        }

        stage('Smoke test build') {
            steps {
                sh 'python -m py_compile one_last_time/*.py || true'
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    def image = "${DOCKERHUB_NAMESPACE}/${APP_NAME}:${IMAGE_TAG}"
                    sh "docker build -t ${image} ."
                }
            }
        }

        stage('Docker Login & Push') {
            steps {
                script {
                    def image = "${DOCKERHUB_NAMESPACE}/${APP_NAME}:${IMAGE_TAG}"
                    sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                    sh "docker push ${image}"
                    // Also tag 'latest'
                    sh "docker tag ${image} ${DOCKERHUB_NAMESPACE}/${APP_NAME}:latest"
                    sh "docker push ${DOCKERHUB_NAMESPACE}/${APP_NAME}:latest"
                }
            }
        }
    }

    post {
        success {
            echo 'Build and push succeeded.'
        }
        failure {
            echo 'Build failed.'
        }
        always {
            sh 'docker logout || true'
        }
    }
}


