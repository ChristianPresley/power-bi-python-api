#!groovy

pipeline {
    agent { 
        docker {
            image 'python:3.9.7'
            reuseNode true
        }
    }
    stages {
        stage('Dev') {
            steps {
                withCredentials([
                    string(credentialsId: 'AZURE_TENANT_ID', variable: 'AZURE_TENANT_ID'),
                    string(credentialsId: 'AZURE_CLIENT_ID', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'AZURE_CLIENT_SECRET', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'AZURE_USERNAME', variable: 'AZURE_USERNAME'),
                    string(credentialsId: 'AZURE_PASSWORD', variable: 'AZURE_PASSWORD'),
                    string(credentialsId: 'KEYVAULT_TENANT_ID', variable: 'KEYVAULT_TENANT_ID'),
                    string(credentialsId: 'KEYVAULT_CLIENT_ID', variable: 'KEYVAULT_CLIENT_ID'),
                    string(credentialsId: 'KEYVAULT_CLIENT_SECRET', variable: 'KEYVAULT_CLIENT_SECRET'),
                    string(credentialsId: 'APPCONFIG_NAME', variable: 'APPCONFIG_NAME'),
                    string(credentialsId: 'KEYVAULT_NAME', variable: 'KEYVAULT_NAME'),
                    string(credentialsId: 'AZURE_STORAGE_CONNECTION_STRING', variable: 'AZURE_STORAGE_CONNECTION_STRING')
                ])
                {
                    withEnv(["HOME=${env.WORKSPACE}"]) {
                        sh "pip install --user -r requirements.txt"
                        sh "python dev.py"
                    }
                }
            }
        }
        stage('Test') {
            steps {
                withCredentials([
                    string(credentialsId: 'AZURE_TENANT_ID', variable: 'AZURE_TENANT_ID'),
                    string(credentialsId: 'AZURE_CLIENT_ID', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'AZURE_CLIENT_SECRET', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'AZURE_USERNAME', variable: 'AZURE_USERNAME'),
                    string(credentialsId: 'AZURE_PASSWORD', variable: 'AZURE_PASSWORD'),
                    string(credentialsId: 'KEYVAULT_TENANT_ID', variable: 'KEYVAULT_TENANT_ID'),
                    string(credentialsId: 'KEYVAULT_CLIENT_ID', variable: 'KEYVAULT_CLIENT_ID'),
                    string(credentialsId: 'KEYVAULT_CLIENT_SECRET', variable: 'KEYVAULT_CLIENT_SECRET'),
                    string(credentialsId: 'APPCONFIG_NAME', variable: 'APPCONFIG_NAME'),
                    string(credentialsId: 'KEYVAULT_NAME', variable: 'KEYVAULT_NAME'),
                    string(credentialsId: 'AZURE_STORAGE_CONNECTION_STRING', variable: 'AZURE_STORAGE_CONNECTION_STRING')
                ])
                {
                    withEnv(["HOME=${env.WORKSPACE}"]) {
                        sh "pip install --user -r requirements.txt"
                        sh "python test.py"
                    }
                }
            }
        }
        stage('Prod') {
            steps {
                withCredentials([
                    string(credentialsId: 'AZURE_TENANT_ID', variable: 'AZURE_TENANT_ID'),
                    string(credentialsId: 'AZURE_CLIENT_ID', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'AZURE_CLIENT_SECRET', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'AZURE_USERNAME', variable: 'AZURE_USERNAME'),
                    string(credentialsId: 'AZURE_PASSWORD', variable: 'AZURE_PASSWORD'),
                    string(credentialsId: 'KEYVAULT_TENANT_ID', variable: 'KEYVAULT_TENANT_ID'),
                    string(credentialsId: 'KEYVAULT_CLIENT_ID', variable: 'KEYVAULT_CLIENT_ID'),
                    string(credentialsId: 'KEYVAULT_CLIENT_SECRET', variable: 'KEYVAULT_CLIENT_SECRET'),
                    string(credentialsId: 'APPCONFIG_NAME', variable: 'APPCONFIG_NAME'),
                    string(credentialsId: 'KEYVAULT_NAME', variable: 'KEYVAULT_NAME'),
                    string(credentialsId: 'AZURE_STORAGE_CONNECTION_STRING', variable: 'AZURE_STORAGE_CONNECTION_STRING')
                ])
                {
                    withEnv(["HOME=${env.WORKSPACE}"]) {
                        sh "pip install --user -r requirements.txt"
                        sh "python prod.py"
                    }
                }
            }
        }
    }
}
