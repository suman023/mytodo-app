pipeline {
    agent any

    environment {
        DOCKER_IMAGE      = "suman2304/mytodo"
        DOCKER_TAG        = "${BUILD_NUMBER}"
        SONAR_PROJECT_KEY = "suman023_mytodo-app"
        SONAR_ORG         = "suman023"
        MANIFEST_REPO     = "https://github.com/suman023/mytodo-k8s-manifests.git"
        EMAIL_TO          = "sumanshit023@gmail.com"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-creds',
                    url: 'https://github.com/suman023/mytodo-app.git'
                echo "Commit: ${GIT_COMMIT}"
            }
        }

        stage('SonarCloud Analysis') {
            steps {
                withSonarQubeEnv('SonarCloud') {
                    sh """
                        sonar-scanner \
                          -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                          -Dsonar.organization=${SONAR_ORG} \
                          -Dsonar.sources=app/ \
                          -Dsonar.host.url=https://sonarcloud.io
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Trivy FS Scan') {
            steps {
                sh """
                    trivy fs \
                        --exit-code 0 \
                        --severity HIGH,CRITICAL \
                        --format table \
                        --output trivy-fs-report.txt \
                        .
                """
                archiveArtifacts artifacts: 'trivy-fs-report.txt', allowEmptyArchive: true
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} -t ${DOCKER_IMAGE}:latest ."
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh """
                    trivy image \
                        --exit-code 0 \
                        --severity HIGH,CRITICAL \
                        --format table \
                        --output trivy-image-report.txt \
                        ${DOCKER_IMAGE}:${DOCKER_TAG}
                """
                archiveArtifacts artifacts: 'trivy-image-report.txt', allowEmptyArchive: true
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE}:latest
                        docker logout
                    """
                }
            }
        }

        stage('Update K8s Manifest') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-creds',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASS'
                )]) {
                    sh """
                        git config --global user.email "sumanshit023@gmail.com"
                        git config --global user.name  "Jenkins CI"

                        rm -rf k8s-manifests
                        git clone https://${GIT_USER}:${GIT_PASS}@github.com/suman023/mytodo-k8s-manifests.git k8s-manifests

                        cd k8s-manifests
                        sed -i 's|image: suman2304/mytodo:.*|image: suman2304/mytodo:${DOCKER_TAG}|g' 05-flask.yaml

                        git add 05-flask.yaml
                        git commit -m "ci: image tag updated to ${DOCKER_TAG} [skip ci]"
                        git push origin main
                    """
                }
                echo "Manifest updated — ArgoCD will now auto-deploy to Minikube"
            }
        }
    }

    post {
        success {
            emailext(
                to: "${EMAIL_TO}",
                subject: "CI SUCCESS: MyToDo Build #${BUILD_NUMBER}",
                body: """
                    <h2>CI Pipeline Successful!</h2>
                    <p><b>Build:</b> #${BUILD_NUMBER}</p>
                    <p><b>Docker Image:</b> ${DOCKER_IMAGE}:${DOCKER_TAG}</p>
                    <p><b>Duration:</b> ${currentBuild.durationString}</p>
                    <p>ArgoCD CD pipeline Minikube mein deploy kar raha hoga.</p>
                    <p><a href="${BUILD_URL}">Jenkins Build dekho</a></p>
                """,
                mimeType: 'text/html'
            )
        }
        failure {
            emailext(
                to: "${EMAIL_TO}",
                subject: "CI FAILED: MyToDo Build #${BUILD_NUMBER}",
                body: """
                    <h2>CI Pipeline Failed!</h2>
                    <p><b>Build:</b> #${BUILD_NUMBER}</p>
                    <p><a href="${BUILD_URL}console">Console log dekho</a></p>
                """,
                mimeType: 'text/html'
            )
        }
        always {
            sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true"
            sh "docker rmi ${DOCKER_IMAGE}:latest || true"
            sh "rm -rf k8s-manifests || true"
            cleanWs()
        }
    }
}
