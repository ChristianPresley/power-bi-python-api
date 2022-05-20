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
                    string(credentialsId: 'SERVICE_ACCOUNT_USERNAME', variable: 'SERVICE_ACCOUNT_USERNAME'),
                    string(credentialsId: 'SERVICE_ACCOUNT_PASSWORD', variable: 'SERVICE_ACCOUNT_PASSWORD'),
                    string(credentialsId: 'POWER_BI_TENANT_ID', variable: 'POWER_BI_TENANT_ID'),
                    string(credentialsId: 'POWER_BI_CLIENT_ID', variable: 'POWER_BI_CLIENT_ID'),
                    string(credentialsId: 'POWER_BI_CLIENT_SECRET', variable: 'POWER_BI_CLIENT_SECRET'),
                    string(credentialsId: 'STORAGE_ACCOUNT_NAME', variable: 'STORAGE_ACCOUNT_NAME'),
                    string(credentialsId: 'STORAGE_ACCOUNT_TENANT_ID', variable: 'STORAGE_ACCOUNT_TENANT_ID'),
                    string(credentialsId: 'STORAGE_ACCOUNT_CLIENT_ID', variable: 'STORAGE_ACCOUNT_CLIENT_ID'),
                    string(credentialsId: 'STORAGE_ACCOUNT_CLIENT_SECRET', variable: 'STORAGE_ACCOUNT_CLIENT_SECRET'),
                    string(credentialsId: 'KEY_VAULT_NAME', variable: 'KEY_VAULT_NAME'),
                    string(credentialsId: 'KEY_VAULT_TENANT_ID', variable: 'KEY_VAULT_TENANT_ID'),
                    string(credentialsId: 'KEY_VAULT_CLIENT_ID', variable: 'KEY_VAULT_CLIENT_ID'),
                    string(credentialsId: 'KEY_VAULT_CLIENT_SECRET', variable: 'KEY_VAULT_CLIENT_SECRET'),
                    string(credentialsId: 'APP_CONFIG_NAME', variable: 'APP_CONFIG_NAME'),
                    string(credentialsId: 'APP_CONFIG_TENANT_ID', variable: 'APP_CONFIG_TENANT_ID'),
                    string(credentialsId: 'APP_CONFIG_CLIENT_ID', variable: 'APP_CONFIG_CLIENT_ID'),
                    string(credentialsId: 'APP_CONFIG_CLIENT_SECRET', variable: 'APP_CONFIG_CLIENT_SECRET')
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
                    string(credentialsId: 'SERVICE_ACCOUNT_USERNAME', variable: 'SERVICE_ACCOUNT_USERNAME'),
                    string(credentialsId: 'SERVICE_ACCOUNT_PASSWORD', variable: 'SERVICE_ACCOUNT_PASSWORD'),
                    string(credentialsId: 'POWER_BI_TENANT_ID', variable: 'POWER_BI_TENANT_ID'),
                    string(credentialsId: 'POWER_BI_CLIENT_ID', variable: 'POWER_BI_CLIENT_ID'),
                    string(credentialsId: 'POWER_BI_CLIENT_SECRET', variable: 'POWER_BI_CLIENT_SECRET'),
                    string(credentialsId: 'STORAGE_ACCOUNT_NAME', variable: 'STORAGE_ACCOUNT_NAME'),
                    string(credentialsId: 'STORAGE_ACCOUNT_TENANT_ID', variable: 'STORAGE_ACCOUNT_TENANT_ID'),
                    string(credentialsId: 'STORAGE_ACCOUNT_CLIENT_ID', variable: 'STORAGE_ACCOUNT_CLIENT_ID'),
                    string(credentialsId: 'STORAGE_ACCOUNT_CLIENT_SECRET', variable: 'STORAGE_ACCOUNT_CLIENT_SECRET'),
                    string(credentialsId: 'KEY_VAULT_NAME', variable: 'KEY_VAULT_NAME'),
                    string(credentialsId: 'KEY_VAULT_TENANT_ID', variable: 'KEY_VAULT_TENANT_ID'),
                    string(credentialsId: 'KEY_VAULT_CLIENT_ID', variable: 'KEY_VAULT_CLIENT_ID'),
                    string(credentialsId: 'KEY_VAULT_CLIENT_SECRET', variable: 'KEY_VAULT_CLIENT_SECRET'),
                    string(credentialsId: 'APP_CONFIG_NAME', variable: 'APP_CONFIG_NAME'),
                    string(credentialsId: 'APP_CONFIG_TENANT_ID', variable: 'APP_CONFIG_TENANT_ID'),
                    string(credentialsId: 'APP_CONFIG_CLIENT_ID', variable: 'APP_CONFIG_CLIENT_ID'),
                    string(credentialsId: 'APP_CONFIG_CLIENT_SECRET', variable: 'APP_CONFIG_CLIENT_SECRET')
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
                    string(credentialsId: 'SERVICE_ACCOUNT_USERNAME', variable: 'SERVICE_ACCOUNT_USERNAME'),
                    string(credentialsId: 'SERVICE_ACCOUNT_PASSWORD', variable: 'SERVICE_ACCOUNT_PASSWORD'),
                    string(credentialsId: 'POWER_BI_TENANT_ID', variable: 'POWER_BI_TENANT_ID'),
                    string(credentialsId: 'POWER_BI_CLIENT_ID', variable: 'POWER_BI_CLIENT_ID'),
                    string(credentialsId: 'POWER_BI_CLIENT_SECRET', variable: 'POWER_BI_CLIENT_SECRET'),
                    string(credentialsId: 'STORAGE_ACCOUNT_NAME', variable: 'STORAGE_ACCOUNT_NAME'),
                    string(credentialsId: 'STORAGE_ACCOUNT_TENANT_ID', variable: 'STORAGE_ACCOUNT_TENANT_ID'),
                    string(credentialsId: 'STORAGE_ACCOUNT_CLIENT_ID', variable: 'STORAGE_ACCOUNT_CLIENT_ID'),
                    string(credentialsId: 'STORAGE_ACCOUNT_CLIENT_SECRET', variable: 'STORAGE_ACCOUNT_CLIENT_SECRET'),
                    string(credentialsId: 'KEY_VAULT_NAME', variable: 'KEY_VAULT_NAME'),
                    string(credentialsId: 'KEY_VAULT_TENANT_ID', variable: 'KEY_VAULT_TENANT_ID'),
                    string(credentialsId: 'KEY_VAULT_CLIENT_ID', variable: 'KEY_VAULT_CLIENT_ID'),
                    string(credentialsId: 'KEY_VAULT_CLIENT_SECRET', variable: 'KEY_VAULT_CLIENT_SECRET'),
                    string(credentialsId: 'APP_CONFIG_NAME', variable: 'APP_CONFIG_NAME'),
                    string(credentialsId: 'APP_CONFIG_TENANT_ID', variable: 'APP_CONFIG_TENANT_ID'),
                    string(credentialsId: 'APP_CONFIG_CLIENT_ID', variable: 'APP_CONFIG_CLIENT_ID'),
                    string(credentialsId: 'APP_CONFIG_CLIENT_SECRET', variable: 'APP_CONFIG_CLIENT_SECRET')
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
