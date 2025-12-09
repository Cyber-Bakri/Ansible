pipeline {
    agent none
    
    environment {
        // Maven configuration
        MAVEN_CLI_OPTS = "-Dmaven.wagon.http.ssl.insecure=true -Dmaven.wagon.http.ssl.allowall=true"
        MAVEN_OPTS = "-Dmaven.repo.local=.m2/repository"
        
        // Application metadata
        METTA_APPLICATION = "springbootfossa"
        METTA_COMPONENT = "fossamavendemo"
        SHIELD_TEAM = "springbootfossa"
        CARID = "9895"
        LOB = "OSPO"
        
        // FOSSA configuration
        FOSSA_API_KEY = credentials('fossa-api-key')  // Store in Jenkins credentials
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
            agent {
                docker {
                    image 'maven:3.8.6-openjdk-11'
                    label 'fossa'  // Equivalent to GitLab tag
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            
            when {
                branch 'main'  // Only run on main branch
            }
            
            steps {
                script {
                    echo "========== Starting Build Stage =========="
                    
                    // Setup certificates and Maven settings
                    sh '''
                        apt-get update && apt-get install -y ca-certificates
                        
                        # Copy Maven settings
                        mkdir -p ~/.m2
                        if [ -f ci/settings.xml ]; then
                            cp ci/settings.xml ~/.m2/settings.xml
                        fi
                        
                        # Copy USB bank root CA certificate
                        if [ -f ci/usbank-root-ca.crt ]; then
                            cp ci/usbank-root-ca.crt /usr/local/share/ca-certificates/usbank-root-ca.crt
                            update-ca-certificates
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
                        mvn dependency:copy-dependencies
                    """
                    
                    // Run the application (test execution)
                    sh '''
                        java -cp "target/cowsay-app-1.0.0.jar:target/dependency/*" com.example.app.Main
                    '''
                }
            }
            
            post {
                success {
                    // Archive artifacts (equivalent to GitLab artifacts)
                    archiveArtifacts artifacts: 'target/**/*', fingerprint: true
                    
                    // Stash artifacts for use in next stage
                    stash includes: 'target/**/*', name: 'build-artifacts'
                    
                    echo "Build stage completed successfully"
                }
                failure {
                    echo "Build stage failed"
                }
            }
        }
        
        stage('FOSSA Security Scan') {
            agent {
                docker {
                    image 'artifactory.us.bank-dns.com:5000/shieldplatform/pipeline-cli-testing/fossa:5563250'
                    label 'shield'  // Equivalent to GitLab tag
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            
            when {
                branch 'main'  // Only run on main branch
            }
            
            steps {
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
            
            post {
                success {
                    echo "FOSSA scan completed successfully - No security issues found"
                }
                failure {
                    echo "FOSSA scan failed - Security vulnerabilities or license issues detected"
                }
                always {
                    // Generate FOSSA report
                    sh '''
                        fossa report attribution --format txt > fossa-report.txt || true
                    '''
                    archiveArtifacts artifacts: 'fossa-report.txt', allowEmptyArchive: true
                }
            }
        }
    }
    
    post {
        always {
            echo "========== Pipeline Execution Complete =========="
            // Clean up workspace
            cleanWs()
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

