#!groovy

pipeline {
    agent { 
        docker {
            image 'python:3.9.7'
            reuseNode true
        }
    }
    stages {
        stage('Power BI Pipeline Creation') {
            steps {
                withCredentials([string(credentialsId: 'AZURE_TENANT_ID', variable: 'AZURE_TENANT_ID'),
                string(credentialsId: 'AZURE_CLIENT_ID', variable: 'AZURE_CLIENT_ID'),
                string(credentialsId: 'AZURE_CLIENT_SECRET', variable: 'AZURE_CLIENT_SECRET')]) {
                    withEnv(["HOME=${env.WORKSPACE}"]) {
                        sh "pip install --user -r requirements.txt"
                        sh "python create_workspaces.py"
                        sh "python create_pipelines.py"
                    }
                }
            }
        }
        stage('Power BI Pipeline Deployment') {
            steps {
                withCredentials([string(credentialsId: 'AZURE_TENANT_ID', variable: 'AZURE_TENANT_ID'),
                string(credentialsId: 'AZURE_CLIENT_ID', variable: 'AZURE_CLIENT_ID'),
                string(credentialsId: 'AZURE_CLIENT_SECRET', variable: 'AZURE_CLIENT_SECRET')]) {
                    withEnv(["HOME=${env.WORKSPACE}"]) {
                        sh "pip install --user -r requirements.txt"
                        sh "python deploy_pipelines.py"
                    }
                }
            }
        }
    }
}
