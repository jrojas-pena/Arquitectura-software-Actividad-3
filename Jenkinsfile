pipeline {
    agent any

    environment {
        REGISTRY = "ghcr.io"
        IMAGE_NAME = "jrojas-pena/arquitectura-software-actividad-3/mcp-graph-svc"
        VERSION = "0.1.${BUILD_NUMBER}"
        GITHUB_TOKEN = credentials('ghcr-token')   // 🔐 ID de la credencial en Jenkins
    }

    stages {
        stage('Checkout') {
            steps {
                sh """
                    rm -rf Arquitectura-software-Actividad-3
                    
                    git clone https://github.com/jrojas-pena/Arquitectura-software-Actividad-3.git Arquitectura-software-Actividad-3
                    
                    ls -la
                    echo "✅ Código obtenido"
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "🐳 Construyendo imagen Docker..."
                    sh """
                    docker build -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} Arquitectura-software-Actividad-3/mcp-graph/services/mcp-graph-svc
                    """
                }
            }
        }

        stage('Login to GHCR') {
            steps {
               withCredentials([string(credentialsId: 'ghcr-token', variable: 'TOKEN')]) {
                     sh '''
                     echo "$TOKEN" | docker login ghcr.io -u jrojas-pena --password-stdin
                     '''
                }
            }
        }

        stage('Push Image') {
            steps {
                script {
                    echo "🚀 Publicando imagen en GHCR..."
                    sh """
                    docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
                    """
                }
            }
        }

        stage('Update Helm Values (Infra Repo)') {
            steps {
                script {
                    echo "📝 Actualizando values.yaml en el repositorio de infraestructura..."
                    sh """
                    rm -rf infra
                    git clone git@github.com:jrojas-pena/arquitectura-software-actividad3-infra.git infra
                    cd infra/mcp-graph/charts/mcp-graph-svc
                    sed -i 's/tag:.*/tag: "${VERSION}"/' values.yaml
                    git config user.name "jenkins"
                    git config user.email "jenkins@local"
                    git add values.yaml
                    git commit -m "Actualiza versión ${VERSION} desde Jenkins"
                    git push origin main || true
                    """
                }
            }
        }

        stage('Post Info') {
            steps {
                echo "✅ Imagen publicada: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
            }
        }
    }

    post {
        success {
            echo "🎉 Pipeline completado exitosamente."
        }
        failure {
            echo "❌ Hubo un error durante la ejecución del pipeline."
        }
    }
}
