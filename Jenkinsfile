pipeline {
    agent { label 'docker-agent' }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DOCKERHUB = 'chanjookim'
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                  python3 -m venv .ci-venv
                  .ci-venv/bin/pip install -r requirements-dev.txt
                  .ci-venv/bin/python -m pytest -q
                '''
            }
        }

        stage('Build') {
            steps {
                script {
                    env.IMAGE_TAG = "build-${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(12)}"
                }

                sh '''
                  docker build -f docker/bot.Dockerfile \
                    -t $DOCKERHUB/chargeops-chatops-bot:$IMAGE_TAG .

                  docker build -f docker/router.Dockerfile \
                    -t $DOCKERHUB/chargeops-alert-router:$IMAGE_TAG .

                  docker build -f docker/csms.Dockerfile \
                    -t $DOCKERHUB/chargeops-mock-csms:$IMAGE_TAG .
                '''
            }
        }

        stage('Push') {
            when {
                branch 'main'
            }

            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    sh '''
                      echo "$DH_TOKEN" | docker login \
                        -u "$DH_USER" --password-stdin

                      docker push $DOCKERHUB/chargeops-chatops-bot:$IMAGE_TAG
                      docker push $DOCKERHUB/chargeops-alert-router:$IMAGE_TAG
                      docker push $DOCKERHUB/chargeops-mock-csms:$IMAGE_TAG

                      docker logout
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'rm -rf .ci-venv || true'
        }
    }
}