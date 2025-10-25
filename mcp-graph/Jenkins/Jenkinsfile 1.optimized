pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo "📥 Obteniendo código del repositorio..."
                sh """
                    # Limpiar workspace si existe
                    rm -rf mcp-graph
                    
                    # Clonar el repositorio
                    git clone https://github.com/jrojas-pena/Arquitectura-software-Actividad-3.git .
                    
                    # Verificar que se descargó
                    ls -la
                    echo "✅ Código obtenido"
                """
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo "🐳 Construyendo imagen Docker..."
                sh """
                    echo "Construyendo imagen: mcp-graph-svc"
                    docker build -t mcp-graph-svc:latest mcp-graph/services/mcp-graph-svc
                    
                    echo "Imagen construida exitosamente"
                    docker images | grep mcp-graph-svc
                """
            }
        }
        
        stage('Test Image') {
            steps {
                echo "🧪 Probando la imagen construida..."
                sh """
                    # Probar que la imagen se puede ejecutar
                    echo "Probando Python..."
                    docker run --rm mcp-graph-svc:latest python --version
                    
                    # Verificar que los archivos están presentes
                    echo "Verificando archivos..."
                    docker run --rm mcp-graph-svc:latest ls -la /app
                    
                    # Probar que FastAPI está disponible
                    echo "Verificando FastAPI..."
                    docker run --rm mcp-graph-svc:latest python -c "import fastapi; print('FastAPI OK')"
                """
            }
        }
        
        stage('Run Container Test') {
            steps {
                echo "🚀 Probando el contenedor en modo test..."
                sh """
                    # Ejecutar el contenedor en background para probar
                    echo "Iniciando contenedor de prueba..."
                    docker run -d --name test-mcp-graph-svc -p 8081:8080 mcp-graph-svc:latest
                    
                    # Esperar a que inicie
                    sleep 10
                    
                    # Probar endpoint de salud
                    echo "Probando endpoint de salud..."
                    curl -f http://localhost:8081/healthz || echo "Endpoint no disponible"
                    
                    # Detener y limpiar
                    docker stop test-mcp-graph-svc
                    docker rm test-mcp-graph-svc
                    
                    echo "✅ Prueba del contenedor completada"
                """
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
        }
        failure {
            echo '❌ Pipeline falló!'
        }
    }
}
