pipeline {
  agent { label 'docker' } // Agente con Docker CLI y buildx (o Docker in Docker)

  options {
    disableConcurrentBuilds()
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  environment {
    // Rutas observadas en tu workflow
    CONTEXT = 'mcp-graph/services/mcp-graph-svc'
    // IMAGE_NAME = ghcr.io/${{ github.repository }}/mcp-graph-svc
    // Lo inferimos dinámicamente desde el remoto 'origin'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh '''
          # Derivar ORG/REPO desde el remoto
          REPO_PATH=$(git remote get-url origin | sed -E 's#.*github.com[:/](.+)\\.git#\\1#')
          echo "REPO_PATH=${REPO_PATH}" > .repo_env
          echo "IMAGE_NAME=ghcr.io/${REPO_PATH}/mcp-graph-svc" >> .repo_env
          cat .repo_env
        '''
        script {
          def envMap = readProperties file: '.repo_env'
          env.IMAGE_NAME = envMap['IMAGE_NAME']
          env.REPO_PATH  = envMap['REPO_PATH']
        }
      }
    }

    stage('Guard: Only main & path filters') {
      when {
        allOf {
          branch 'main'
          anyOf {
            changeset "mcp-graph/services/mcp-graph-svc/**"
            changeset "mcp-graph/charts/mcp-graph-svc/**"
            changeset ".github/workflows/ci-cd.yaml"
          }
        }
      }
      steps {
        echo "Cambios válidos en main: continuando pipeline…"
      }
    }

    stage('Login GHCR') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'GHCR_CREDS', usernameVariable: 'GH_USER', passwordVariable: 'GH_PAT')]) {
          sh '''
            echo "${GH_PAT}" | docker login ghcr.io -u "${GH_USER}" --password-stdin
          '''
        }
      }
    }

    stage('Docker meta (tags)') {
      when { branch 'main' }
      steps {
        sh '''
          # Equivalente a docker/metadata-action@v5 con type=sha y type=ref,event=branch
          # Jenkins multibranch exporta BRANCH_NAME y GIT_COMMIT
          SHA_TAG="${GIT_COMMIT}"
          # Normaliza nombre de rama para tag
          BRANCH_TAG=$(echo "${BRANCH_NAME:-main}" | tr '[:upper:]' '[:lower:]' | tr '/' '-')
          echo "TAGS=${IMAGE_NAME}:${SHA_TAG},${IMAGE_NAME}:${BRANCH_TAG}" > .tags_env
          cat .tags_env
        '''
        script {
          def t = readProperties file: '.tags_env'
          env.TAGS = t['TAGS']
        }
      }
    }

    stage('Build & Push Image') {
      when { branch 'main' }
      steps {
        sh '''
          set -e
          # Asegura buildx
          docker buildx create --use || true
          # Construye y publica
          IFS=',' read -r TAG1 TAG2 <<EOF
${TAGS}
EOF
          echo "Building and pushing: ${TAG1} and ${TAG2}"
          docker buildx build \
            --platform linux/amd64 \
            --push \
            -t "${TAG1}" \
            -t "${TAG2}" \
            "${CONTEXT}"
        '''
      }
    }

    stage('Bump helm values to commit SHA') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'GIT_PUSH_CREDS', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
          sh '''
            set -e
            IMAGE_TAG="${GIT_COMMIT}"
            FILE="mcp-graph/charts/mcp-graph-svc/values.yaml"

            # Actualiza el tag dentro de values.yaml (equivalente a tu sed)
            sed -i "s#tag: \\".*\\"#tag: \\"${IMAGE_TAG}\\"#g" "${FILE}"

            git config user.name  "github-actions"
            git config user.email "github-actions@users.noreply.github.com"

            # Reescribe la URL de origin con credenciales para poder pushear
            ORIGIN=$(git remote get-url origin | sed -E "s#https://github.com/#https://${GIT_USER}:${GIT_TOKEN}@github.com/#")
            git remote set-url origin "${ORIGIN}"

            git add "${FILE}" || true
            git commit -m "bump image tag to ${IMAGE_TAG}" || echo "no changes"
            git push || true
          '''
        }
      }
    }
  }

  post {
    success {
      echo "Éxito. Imagen(es): ${env.TAGS}"
    }
    always {
      echo "Build URL: ${env.BUILD_URL}"
    }
  }
}
