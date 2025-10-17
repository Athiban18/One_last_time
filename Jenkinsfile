pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_NAMESPACE   = "cheenu181"
        APP_NAME              = "one_last_time"
        IMAGE_TAG             = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    triggers {
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
                sh 'python3 --version'
                sh 'pip3 --version'
            }
        }

        stage('Install deps (optional)') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r one_last_time/requirements.txt
                '''
            }
        }

        stage('Smoke test build') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m py_compile one_last_time/*.py
                '''
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
                    sh "docker tag ${image} ${DOCKERHUB_NAMESPACE}/${APP_NAME}:latest"
                    sh "docker push ${DOCKERHUB_NAMESPACE}/${APP_NAME}:latest"
                    sh 'docker logout'
                }
            }
        }
    }

    post {
        success {
            echo '✅ Build and push succeeded.'
        }
        failure {
            echo '❌ Build failed.'
        }
    }
}
