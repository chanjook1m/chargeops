pipeline {
  agent { label 'chargeops-agent' }

  options {
    timestamps()
    disableConcurrentBuilds()
    skipDefaultCheckout(true)
  }
  triggers { pollSCM('H/5 * * * *') }
  environment { REGISTRY = 'chanjookim' }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        script {
          def sha = sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim()
          env.IMAGE_TAG = "build-${env.BUILD_NUMBER}-${sha}"
          echo "IMAGE_TAG=${env.IMAGE_TAG}"
        }
      }
    }
    stage('Test (Python 3.12)') {
      steps {
        sh '''
          set -eu
          python3.12 -m venv .ci-venv
          .ci-venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
          .ci-venv/bin/python -m pytest -q
        '''
      }
    }
    stage('Docker Build: three independent images') {
      steps {
        sh '''
          set -eu
          docker build --pull -f docker/chatops-bot.Dockerfile \
            -t "$REGISTRY/chargeops-chatops-bot:$IMAGE_TAG" \
            -t "$REGISTRY/chargeops-chatops-bot:dev" .

          # 실제 GitHub 파일명은 router.Dockerfile 입니다.
          docker build --pull -f docker/router.Dockerfile \
            -t "$REGISTRY/chargeops-alert-router:$IMAGE_TAG" \
            -t "$REGISTRY/chargeops-alert-router:dev" .

          docker build --pull -f docker/mock-csms.Dockerfile \
            -t "$REGISTRY/chargeops-mock-csms:$IMAGE_TAG" \
            -t "$REGISTRY/chargeops-mock-csms:dev" .
        '''
      }
    }
    stage('Docker Hub Login and Push') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-write',
          usernameVariable: 'DH_USER',
          passwordVariable: 'DH_TOKEN'
        )]) {
          sh '''
            set -eu
            set +x
            export DOCKER_CONFIG="$(mktemp -d)"
            trap 'rm -rf "$DOCKER_CONFIG"' EXIT
            printf '%s' "$DH_TOKEN" | docker login docker.io -u "$DH_USER" --password-stdin
            for NAME in chargeops-chatops-bot chargeops-alert-router chargeops-mock-csms; do
              docker push "$REGISTRY/$NAME:$IMAGE_TAG"
              docker push "$REGISTRY/$NAME:dev"
            done
            docker logout docker.io
          '''
        }
      }
    }
  }
  post {
    always { sh 'rm -rf .ci-venv || true' }
    success { echo "Push completed: ${env.IMAGE_TAG}" }
  }
}