// ╔═══════════════════════════════════════════════════════╗
// ║         JENKINSFILE - MyToDo App                      ║
// ║                                                       ║
// ║  1.  Code Download   (GitHub)                         ║
// ║  2.  Python Check    (python/pip version)             ║
// ║  3.  pip install     (packages)                       ║
// ║  4.  SonarCloud      (code quality)                   ║
// ║  5.  Docker Build    (image)                          ║
// ║  6.  Trivy Check     (trivy version)                  ║
// ║  7.  Trivy Scan      (security check)                 ║
// ║  8.  Docker Login    (dockerhub)                      ║
// ║  9.  Docker Push     (image upload)                   ║
// ║  10. Update Manifest (ArgoCD GitOps → Minikube)       ║
// ║  11. Email           (success/fail)                   ║
// ╚═══════════════════════════════════════════════════════╝

pipeline {

    agent any

    // ═══════════════════════════════════════════════════
    // VARIABLES
    // ═══════════════════════════════════════════════════
    environment {

        // App name
        APP_NAME = "mytodo"

        // DockerHub image name
        DOCKER_IMAGE = "suman2304/mytodo"

        // Image version - BUILD_NUMBER (1,2,3...)
        DOCKER_TAG = "v${BUILD_NUMBER}"

        // SonarCloud project details
        SONAR_PROJECT = "suman023_mytodo-app"
        SONAR_ORG     = "suman023"

        // Notification email
        EMAIL_TO = "sumanshit023@gmail.com"

        // K8s Manifest repo (ArgoCD watch karta hai)
        MANIFEST_REPO = "https://github.com/suman023/mytodo-k8s-manifests.git"
    }

    // ═══════════════════════════════════════════════════
    // OPTIONS - pipeline settings
    // ═══════════════════════════════════════════════════
    options {
        // Logs mein time dikhao
        timestamps()

        // Ek time pe ek hi build
        disableConcurrentBuilds()

        // Sirf 10 builds rakho
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    // ═══════════════════════════════════════════════════
    // STAGES - pipeline steps
    // ═══════════════════════════════════════════════════
    stages {

        // ─────────────────────────────────────────────
        // STEP 1 - GitHub se code download
        // ─────────────────────────────────────────────
        stage('1 - Code Download') {
            steps {
                echo '>>> STEP 1: Code download ...'

                checkout scm

                echo '>>> STEP 1: Done!'
            }
        }

        // ─────────────────────────────────────────────
        // STEP 2 - Python aur pip version check
        // ─────────────────────────────────────────────
        stage('2 - Verify Python') {
            steps {
                echo '>>> STEP 2: Python check ...'

                sh '''
                    which python3
                    python3 --version
                    pip3 --version
                '''

                echo '>>> STEP 2: Done!'
            }
        }

        // ─────────────────────────────────────────────
        // STEP 3 - pip install (Python packages)
        // ─────────────────────────────────────────────
        stage('3 - Install Packages') {
            steps {
                echo '>>> STEP 3: pip installing ...'

                sh '''
                    pip3 install -r app/requirements.txt --break-system-packages
                '''

                echo '>>> STEP 3: Done!'
            }
        }

        // ─────────────────────────────────────────────
        // STEP 4 - SonarCloud Scan
        // Results: https://sonarcloud.io/organizations/suman023
        // ─────────────────────────────────────────────
        stage('4 - SonarCloud Scan') {
            steps {
                echo '>>> STEP 4: SonarCloud scanning ...'

                withSonarQubeEnv('SonarCloud') {
                    sh """
                        sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT} \
                        -Dsonar.organization=${SONAR_ORG} \
                        -Dsonar.sources=app/ \
                        -Dsonar.exclusions=**/templates/**,**/__pycache__/** \
                        -Dsonar.python.version=3 \
                        -Dsonar.host.url=https://sonarcloud.io
                    """
                }

                echo '>>> STEP 4: Done!'
            }
        }

        // ─────────────────────────────────────────────
        // STEP 5 - Docker Image build
        // ─────────────────────────────────────────────
        stage('5 - Docker Build') {
            steps {
                echo '>>> STEP 5: Docker image build...'

                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag  ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"

                echo ">>> STEP 5: Done! Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
        }

        // ─────────────────────────────────────────────
        // STEP 6 - Trivy Version Check
        // ─────────────────────────────────────────────
        stage('6 - Verify Trivy') {
            steps {
                echo '>>> STEP 6: Trivy version check...'

                sh 'trivy --version'

                echo '>>> STEP 6: Done!'
            }
        }

        // ─────────────────────────────────────────────
        // STEP 7 - Trivy Security Scan
        // Report: trivy-reports/trivy-report.html
        // ─────────────────────────────────────────────
        stage('7 - Trivy Security Scan') {
            steps {
                echo '>>> STEP 7: Security scanning...'

                sh '''
                    mkdir -p trivy-reports

                    if [ ! -f /usr/local/share/trivy/templates/html.tpl ]; then
                        sudo mkdir -p /usr/local/share/trivy/templates
                        sudo wget \
                        https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl \
                        -O /usr/local/share/trivy/templates/html.tpl
                    fi

                    trivy image \
                    --severity HIGH,CRITICAL \
                    --format template \
                    --template "@/usr/local/share/trivy/templates/html.tpl" \
                    -o trivy-reports/trivy-report.html \
                    ${DOCKER_IMAGE}:latest
                '''

                echo '>>> STEP 7: Done!'
            }

            post {
                always {
                    // HTML report Jenkins mein save karo
                    // Jenkins job → Artifacts mein dikhega
                    archiveArtifacts artifacts: 'trivy-reports/trivy-report.html',
                                     fingerprint: true
                }
            }
        }

        // ─────────────────────────────────────────────
        // STEP 8 - DockerHub Login
        // Credentials: Manage Jenkins → Credentials
        //   ID: dockerhub-credentials
        // ─────────────────────────────────────────────
        stage('8 - Docker Login') {
            steps {
                echo '>>> STEP 8: DockerHub login...'

                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }

                echo '>>> STEP 8: Done!'
            }
        }

        // ─────────────────────────────────────────────
        // STEP 9 - Docker Push to DockerHub
        // ─────────────────────────────────────────────
        stage('9 - Docker Push') {
            steps {
                echo '>>> STEP 9: Image DockerHub pe push...'

                sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                sh "docker push ${DOCKER_IMAGE}:latest"

                echo '>>> STEP 9: Done!'
            }
        }

        // ─────────────────────────────────────────────
        // STEP 10 - K8s Manifest Update (GitOps)
        // Jenkins ka kaam yahan khatam
        // ArgoCD automatically Minikube mein deploy karega
        // ─────────────────────────────────────────────
        stage('10 - Update K8s Manifest') {
            steps {
                echo '>>> STEP 10: K8s manifest update (ArgoCD handoff)...'

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
                        git commit -m "ci: image updated to ${DOCKER_TAG} [skip ci]"
                        git push origin main
                    """
                }

                echo '>>> STEP 10: Done! ArgoCD will deploy to Minikube automatically.'
            }
        }

    } // end stages

    // ═══════════════════════════════════════════════════
    // POST ACTIONS
    // ═══════════════════════════════════════════════════
    post {

        always {
            echo '>>> Cleanup...'
            sh 'docker logout || true'
            sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true"
            sh "docker rmi ${DOCKER_IMAGE}:latest || true"
            sh 'rm -rf k8s-manifests || true'
            cleanWs()
        }

        success {
            echo '🎉 BUILD SUCCESSFUL!'

            mail(
                to: "${EMAIL_TO}",
                subject: "✅ SUCCESS: MyToDo Build #${env.BUILD_NUMBER}",
                body: """
Build Successful! 🎉

Project   : ${env.JOB_NAME}
Build No  : #${env.BUILD_NUMBER}
Image     : ${DOCKER_IMAGE}:${DOCKER_TAG}
Build URL : ${env.BUILD_URL}

SonarCloud : https://sonarcloud.io/organizations/suman023
DockerHub  : https://hub.docker.com/r/suman2304/mytodo
ArgoCD     : ArgoCD ne Minikube mein deploy kar diya hoga
                """
            )
        }

        failure {
            echo '❌ BUILD FAILED!'

            mail(
                to: "${EMAIL_TO}",
                subject: "❌ FAILED: MyToDo Build #${env.BUILD_NUMBER}",
                body: """
Build Failed! ❌

Project   : ${env.JOB_NAME}
Build No  : #${env.BUILD_NUMBER}
Error Log : ${env.BUILD_URL}console

Please check!
                """
            )
        }

    } // end post

} // end pipeline
