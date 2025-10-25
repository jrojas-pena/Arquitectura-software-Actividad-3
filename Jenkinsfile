pipeline {
    agent any
    
    environment {
        IMAGE_NAME = "ghcr.io/${GITHUB_REPOSITORY}/mcp-graph-svc"
        CONTEXT = "mcp-graph/services/mcp-graph-svc"
        DOCKER_REGISTRY = "ghcr.io"
        HELM_CHART_PATH = "mcp-graph/charts/mcp-graph-svc"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
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
            }
        }
        
        stage('Docker Login') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'ghcr-token', variable: 'GHCR_TOKEN')]) {
                        sh """
                            echo "${GHCR_TOKEN}" | docker login ${DOCKER_REGISTRY} -u ${GITHUB_ACTOR} --password-stdin
                        """
                    }
                }
            }
        }
        
        stage('Build & Push Docker Image') {
            steps {
                script {
                    def imageTags = [
                        "${IMAGE_NAME}:${env.GIT_COMMIT_SHA}",
                        "${IMAGE_NAME}:${env.GIT_BRANCH}"
                    ]
                    
                    def tagsString = imageTags.join(',')
                    
                    sh """
                        docker build -t ${IMAGE_NAME}:${env.GIT_COMMIT_SHA} ${CONTEXT}
                        docker tag ${IMAGE_NAME}:${env.GIT_COMMIT_SHA} ${IMAGE_NAME}:${env.GIT_BRANCH}
                        
                        # Push images
                        docker push ${IMAGE_NAME}:${env.GIT_COMMIT_SHA}
                        docker push ${IMAGE_NAME}:${env.GIT_BRANCH}
                    """
                }
            }
        }
        
        stage('Update Helm Values') {
            steps {
                script {
                    sh """
                        # Update the image tag in values.yaml
                        sed -i 's#tag: ".*"#tag: "${env.GIT_COMMIT_SHA}"#g' ${HELM_CHART_PATH}/values.yaml
                        
                        # Configure git
                        git config user.name "jenkins"
                        git config user.email "jenkins@example.com"
                        
                        # Add and commit changes
                        git add ${HELM_CHART_PATH}/values.yaml
                        git commit -m "bump image tag to ${env.GIT_COMMIT_SHA}" || echo "no changes"
                        
                        # Push changes
                        git push origin ${env.GIT_BRANCH} || echo "push failed or no changes"
                    """
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh """
                        # Install/upgrade the Helm chart
                        helm upgrade --install mcp-graph-svc ${HELM_CHART_PATH} \\
                            --set image.repository=${IMAGE_NAME} \\
                            --set image.tag=${env.GIT_COMMIT_SHA} \\
                            --namespace default \\
                            --create-namespace
                    """
                }
            }
        }
    }
    
    post {
        always {
            // Clean up Docker images to save space
            sh 'docker system prune -f'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
