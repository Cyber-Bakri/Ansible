@Library('enterprise-pipeline-library@master')_
import com.usbank.*

pipeline {
    agent {
        kubernetes {
            yaml """
${easyAgents(easyTemplate: 'java')}
---
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: fossa
    image: artifactory.us.bank-dns.com:5000/shieldplatform/pipeline-cli-testing/fossa:5563250
    command:
    - cat
    tty: true
"""
        }
    }
    
    environment {
        // Line of Business
        LOB = "OSPO"
        
        // Maven configuration
        MAVEN_SETTINGS = "\${MAVEN_SETTINGS_XML}"
        MAVEN_CLI_OPTS = "--batch-mode --errors --fail-at-end -X"
        
        // Artifactory configuration
        ARTIFACTORY_URL = "https://artifactory.us.bank-dns.com/artifactory/ospo-prebundle-maven-release-local"
        ARTIFACTORY_KEY = credentials('artifactory-key')
        
        // Application metadata
        METTA_APPLICATION = "springbootfossa"
        METTA_COMPONENT = "fossamavendemo"
        SHIELD_TEAM = "springbootfossa"
        CARID = "9895"
        FOB = "line0fBiz"
        
        // FOSSA configuration
        FOSSA_API_KEY = credentials('fossa-api-key')
        FOSSA_RELEASE_GROUPS = "Fossa-Maven-Demo"
        FOSSA_RELEASE_VERSION = "1.1.0"
        FOSSA_TEAM = "9895_FOSSA"
    }
    
    options {
        // Build retention - keep builds for 30 days
        buildDiscarder(logRotator(daysToKeepStr: '30', numToKeepStr: '10'))
        // Timeout for entire pipeline
        timeout(time: 1, unit: 'HOURS')
        // Disable concurrent builds
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Build Application') {
            when {
                branch 'main'  // Only run on main branch
            }
            
            steps {
                container('java') {
                    script {
                        echo "========== Starting Build Stage =========="
                        
                        // Setup certificates and Maven settings from ci/ folder
                        sh '''
                            # Copy Maven settings from repository
                            mkdir -p ~/.m2
                            if [ -f ci/settings.xml ]; then
                                cp ci/settings.xml ~/.m2/settings.xml
                                echo "[INFO] Copied Maven settings from ci/settings.xml"
                            fi
                            
                            # Copy US Bank root CA certificate from repository
                            if [ -f ci/usbank-root-ca.crt ]; then
                                cp ci/usbank-root-ca.crt /usr/local/share/ca-certificates/usbank-root-ca.crt
                                update-ca-certificates
                                echo "[INFO] Installed US Bank root CA certificate"
                            fi
                            
                            # Display Java version
                            echo "[INFO] Java version: $(java -version 2>&1 | head -n 1)"
                        '''
                        
                        // Build the application
                        sh """
                            mvn clean package -DskipTests ${MAVEN_CLI_OPTS}
                        """
                        
                        // Copy dependencies
                        sh """
                            mvn dependency:copy-dependencies ${MAVEN_CLI_OPTS}
                        """
                        
                        // Run the application (test execution)
                        sh '''
                            java -cp "target/cowsay-app-1.0.0.jar:target/dependency/*" com.example.app.Main
                        '''
                    }
                }
            }
            
            post {
                success {
                    // Archive artifacts
                    archiveArtifacts artifacts: 'target/**/*', fingerprint: true
                    
                    // Stash artifacts for use in next stage
                    stash includes: 'target/**/*,pom.xml,.fossa.yml', name: 'build-artifacts'
                    
                    echo "Build stage completed successfully"
                }
                failure {
                    echo "Build stage failed"
                }
            }
        }
        
        stage('FOSSA Security Scan') {
            when {
                branch 'main'  // Only run on main branch
            }
            
            steps {
                container('fossa') {
                    script {
                        echo "========== Starting FOSSA Scan Stage =========="
                        
                        // Unstash artifacts from previous stage
                        unstash 'build-artifacts'
                        
                        // Run FOSSA scan
                        sh '''
                            # Initialize FOSSA
                            fossa init
                            
                            # Run FOSSA analysis
                            fossa analyze --team="${FOSSA_TEAM}" \
                                         --title="${FOSSA_RELEASE_GROUPS}" \
                                         --revision="${FOSSA_RELEASE_VERSION}" \
                                         --project="${METTA_APPLICATION}"
                            
                            # Test for security issues
                            fossa test
                        '''
                    }
                }
            }
            
            post {
                success {
                    echo "FOSSA scan completed successfully - No security issues found"
                }
                failure {
                    echo "FOSSA scan failed - Security vulnerabilities or license issues detected"
                }
                always {
                    script {
                        container('fossa') {
                            // Generate FOSSA report
                            sh '''
                                fossa report attribution --format txt > fossa-report.txt || true
                            '''
                        }
                        archiveArtifacts artifacts: 'fossa-report.txt', allowEmptyArchive: true
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "========== Pipeline Execution Complete =========="
            // Note: cleanWs() not needed with Kubernetes agents - pods are ephemeral
        }
        success {
            echo "✅ Pipeline completed successfully"
            // Add notification here (email, Slack, etc.)
        }
        failure {
            echo "❌ Pipeline failed"
            // Add notification here (email, Slack, etc.)
        }
    }
}
