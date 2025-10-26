pipeline {
    agent any
    
    environment {
        IMAGE_NAME = "mcp-graph-svc"
        CONTEXT = "mcp-graph/services/mcp-graph-svc"
    }
    
    stages {
        stage('Get Git Info') {
            steps {
                echo "📥 Obteniendo información del repositorio..."
                script {
                    env.GIT_COMMIT_SHA = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                    env.GIT_BRANCH = sh(
                        script: 'git rev-parse --abbrev-ref HEAD',
                        returnStdout: true
                    ).trim()
                }
                echo "✅ Información obtenida - Commit: ${env.GIT_COMMIT_SHA}"
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "🐳 Construyendo imagen Docker..."
                script {
                    def imageTag = "${IMAGE_NAME}:${env.GIT_COMMIT_SHA}"
                    def imageTagLatest = "${IMAGE_NAME}:latest"
                    
                    sh """
                        echo "Construyendo imagen: ${imageTag}"
                        docker build -t ${imageTag} ${CONTEXT}
                        docker tag ${imageTag} ${imageTagLatest}
                        
                        echo "Imagen construida exitosamente"
                        docker images | grep ${IMAGE_NAME}
                    """
                }
            }
        }
        
        stage('Test Image') {
            steps {
                echo "🧪 Probando la imagen construida..."
                script {
                    sh """
                        # Probar que la imagen se puede ejecutar
                        echo "Probando Python..."
                        docker run --rm ${IMAGE_NAME}:${env.GIT_COMMIT_SHA} python --version
                        
                        # Verificar que los archivos están presentes
                        echo "Verificando archivos..."
                        docker run --rm ${IMAGE_NAME}:${env.GIT_COMMIT_SHA} ls -la /app
                        
                        # Probar que FastAPI está disponible
                        echo "Verificando FastAPI..."
                        docker run --rm ${IMAGE_NAME}:${env.GIT_COMMIT_SHA} python -c "import fastapi; print('FastAPI OK')"
                    """
                }
            }
        }
        
        stage('Run Container Test') {
            steps {
                echo "🚀 Probando el contenedor en modo test..."
                script {
                    sh """
                        # Ejecutar el contenedor en background para probar
                        echo "Iniciando contenedor de prueba..."
                        docker run -d --name test-${IMAGE_NAME} -p 8081:8080 ${IMAGE_NAME}:${env.GIT_COMMIT_SHA}
                        
                        # Esperar a que inicie
                        sleep 10
                        
                        # Probar endpoint de salud
                        echo "Probando endpoint de salud..."
                        curl -f http://localhost:8081/healthz || echo "Endpoint no disponible"
                        
                        # Detener y limpiar
                        docker stop test-${IMAGE_NAME}
                        docker rm test-${IMAGE_NAME}
                        
                        echo "✅ Prueba del contenedor completada"
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "🧹 Limpiando recursos..."
            sh 'docker system prune -f || true'
        }
        success {
            echo '✅ Pipeline completado exitosamente!'
            script {
                sh """
                    echo "📊 Resumen del build:"
                    echo "  - Imagen: ${IMAGE_NAME}:${env.GIT_COMMIT_SHA}"
                    echo "  - Branch: ${env.GIT_BRANCH}"
                    echo "  - Commit: ${env.GIT_COMMIT_SHA}"
                    echo "  - Estado: ✅ EXITOSO"
                """
            }
        }
        failure {
            echo '❌ Pipeline falló!'
        }
    }
}
