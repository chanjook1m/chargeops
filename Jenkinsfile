pipeline {
  agent {
    label 'rocky9'
  }

  options {
    timestamps()
    disableConcurrentBuilds()
    skipDefaultCheckout(true)
  }

  triggers {
    pollSCM('H/2 * * * *')
  }

  environment {
    REGISTRY = 'chanjookim'
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm

        script {
          def sha = sh(
            script: 'git rev-parse --short=12 HEAD',
            returnStdout: true
          ).trim()

          env.IMAGE_TAG = "build-${env.BUILD_NUMBER}-${sha}"

          echo "IMAGE_TAG=${env.IMAGE_TAG}"
        }
      }
    }

    stage('Test') {
      steps {
        sh '''
          set -eu

          python3 -m venv .ci-venv

          .ci-venv/bin/python -m pip install --upgrade pip

          .ci-venv/bin/pip install \
            -r requirements.txt \
            -r requirements-dev.txt

          .ci-venv/bin/python -m pytest -q
        '''
      }
    }

    stage('Build service images') {
      steps {
        sh '''
          set -eu

          docker build --pull \
            -f docker/chatops-bot.Dockerfile \
            -t $REGISTRY/chargeops-chatops-bot:$IMAGE_TAG \
            -t $REGISTRY/chargeops-chatops-bot:dev \
            .

          docker build --pull \
            -f docker/alert-router.Dockerfile \
            -t $REGISTRY/chargeops-alert-router:$IMAGE_TAG \
            -t $REGISTRY/chargeops-alert-router:dev \
            .

          docker build --pull \
            -f docker/mock-csms.Dockerfile \
            -t $REGISTRY/chargeops-mock-csms:$IMAGE_TAG \
            -t $REGISTRY/chargeops-mock-csms:dev \
            .
        '''
      }
    }

    stage('Docker Login') {
      steps {
        withCredentials([
          usernamePassword(
            credentialsId: 'dockerhub-write',
            usernameVariable: 'DH_USER',
            passwordVariable: 'DH_TOKEN'
          )
        ]) {

          sh '''
            set +x
            echo "$DH_TOKEN" | docker login \
              -u "$DH_USER" \
              --password-stdin
          '''
        }
      }
    }

    stage('Push service images') {
      steps {
        sh '''
          set -eu

          for svc in \
            chargeops-chatops-bot \
            chargeops-alert-router \
            chargeops-mock-csms
          do
            docker push $REGISTRY/$svc:$IMAGE_TAG
            docker push $REGISTRY/$svc:dev
          done
        '''
      }
    }
  }

  post {

    always {

      sh '''
        docker logout >/dev/null 2>&1 || true
        rm -rf .ci-venv || true
      '''

      cleanWs(
        deleteDirs: true,
        disableDeferredWipeout: true
      )
    }

    success {
      echo "Build Success"
      echo "Image Tag : ${IMAGE_TAG}"
    }

    failure {
      echo "Build Failed"
    }
  }
}