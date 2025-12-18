@Library('enterprise-pipeline-library@FossaStaging2')_
import com.usbank.*

pipeline {
    agent {
        kubernetes {
            yaml easyAgents(easyTemplate: 'java')
        }
    }
    
    environment {
        LOB = "OSPO"
        CARID = "9895"
        MAVEN_SETTINGS = "${MAVEN_SETTINGS_XML}"
        MAVEN_CLI_OPTS = "-Dmaven.wagon.http.ssl.insecure=true -Dmaven.wagon.http.ssl.allowall=true"
        MAVEN_OPTS = "-Dmaven.repo.local=.m2/repository"
        METTA_APPLICATION = "springbootfossa"
        METTA_COMPONENT = "fossamavendemo"
        SHIELD_TEAM = "springbootfossa"
        ARTIFACTORY_KEY = credentials('artifactory-key')
    }

    stages {
        
        // Step 1: Build cowsay-app
        stage('Maven Build') {
            steps {
                container('java') {
                    configFileProvider([configFile(fileId: 'maven-poc-xml', variable: 'MAVEN_SETTINGS')]) {
                        sh '''
                            # Update CA certificates
                            mkdir -p ~/.m2
                            cp ci/settings.xml ~/.m2/settings.xml
                            cp ci/usbank-root-ca.crt /usr/local/share/ca-certificates/usbank-root-ca.crt
                            update-ca-certificates
                            
                            # Display Java version
                            echo "[INFO] Java version"
                            java -version
                            echo "[INFO] JAVA_HOME: $JAVA_HOME"
                            
                            # Maven build with Java version override
                            mvn clean package -DskipTests $MAVEN_CLI_OPTS -Dmaven.compiler.source=11 -Dmaven.compiler.target=11 -Dmaven.compiler.release=11
                            
                            # Copy dependencies
                            mvn dependency:copy-dependencies
                            
                            # Run Java application
                            java -cp "target/cowsay-app-1.0.0.jar:target/dependency/*" com.example.app.Main
                        '''
                    }
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: 'target/', fingerprint: true, allowEmptyArchive: true
                }
            }
        }

        // Step 2: Fossa scan stage
        stage('Fossa Scan') {
            steps {
                container('fossa') {
                    configFileProvider([configFile(fileId: 'maven-poc-xml', variable: 'MAVEN_SETTINGS')]) {
                        sh 'cat $MAVEN_SETTINGS > testsettings.xml'
                        fossaScan(
                            releaseGroups: ['Fossa-Maven-Demo'],
                            team: '9895_FOSSA',
                            version: '1.1.0',
                            debug: true
                        )
                    }
                }
            }
        }

    }
    
    post {
        always {
            archiveArtifacts artifacts: "fossa.debug.json.gz,fossa.telemetry.json", fingerprint: true, allowEmptyArchive: true
        }
    }
}
