#!/usr/bin/env python

import os

class BaseConfig(object):
    # 'ServiceAccount' == TRUE or 'ServicePrincipal' == FALSE
    auth_mode = False
    
    # Log with email address using internet browser
    LOG_WITH_PERSONAL_ACCOUNT = False 
    
    if auth_mode and not LOG_WITH_PERSONAL_ACCOUNT:
        AUTHENTICATION_MODE = 'ServiceAccount'
        SERVICE_ACCOUNT_USERNAME = os.getenv('SERVICE_ACCOUNT_USERNAME')
        SERVICE_ACCOUNT_PASSWORD = os.getenv('SERVICE_ACCOUNT_PASSWORD')
    elif not auth_mode and not LOG_WITH_PERSONAL_ACCOUNT:
        AUTHENTICATION_MODE = 'ServicePrincipal'
        SERVICE_ACCOUNT_USERNAME = None
        SERVICE_ACCOUNT_PASSWORD = None
    
    # # Azure Tenant ID for authentication
    POWER_BI_TENANT_ID = os.getenv('POWER_BI_TENANT_ID')

    # # Client ID of the App Registration / Service Principal
    POWER_BI_CLIENT_ID = os.getenv('POWER_BI_CLIENT_ID')

    # # Client secret of the App Registration / Service Principal
    # # Only required for ServicePrincipal
    POWER_BI_CLIENT_SECRET = os.getenv('POWER_BI_CLIENT_SECRET')
    # # Storage Account Configuration
    try:
        STORAGE_ACCOUNT_NAME = os.environ['STORAGE_ACCOUNT_NAME']
        STORAGE_ACCOUNT_URI = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        STORAGE_BLOB_CONTAINER_NAME = "powerbi-container"

        # ## Storage Account Tenant ID
        STORAGE_ACCOUNT_TENANT_ID = os.environ['STORAGE_ACCOUNT_TENANT_ID']

        # ## Storage Account Client ID of the App Registration / Service Principal
        STORAGE_ACCOUNT_CLIENT_ID = os.environ['STORAGE_ACCOUNT_CLIENT_ID']

        # ## Storage Account Client Secret of the App Registration / Service Principal
        STORAGE_ACCOUNT_CLIENT_SECRET = os.environ['STORAGE_ACCOUNT_CLIENT_SECRET']
    except:
        STORAGE_ACCOUNT_NAME = None
        STORAGE_ACCOUNT_TENANT_ID = None
        STORAGE_ACCOUNT_CLIENT_ID = None

    try:
        # # Key Vault Configuration
        KEY_VAULT_NAME = os.environ['KEY_VAULT_NAME']
        KEY_VAULT_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net"

        ## Key Vault Tenant ID
        KEY_VAULT_TENANT_ID = os.environ['KEY_VAULT_TENANT_ID']

        ## Key Vault Client ID of the App Registration / Service Principal
        KEY_VAULT_CLIENT_ID = os.environ['KEY_VAULT_CLIENT_ID']

        ## Key Vault Client Secret of the App Registration / Service Principal
        KEY_VAULT_CLIENT_SECRET = os.environ['KEY_VAULT_CLIENT_SECRET']
    except:
        KEY_VAULT_NAME = None
        KEY_VAULT_URI = None
        KEY_VAULT_TENANT_ID = None
        KEY_VAULT_CLIENT_ID = None
        KEY_VAULT_CLIENT_SECRET = None
    
    try:
        # App Config Configuration
        APP_CONFIG_NAME = os.environ['APP_CONFIG_NAME']
        APP_CONFIG_URI = f"https://{APP_CONFIG_NAME}.azconfig.io"

        ## App Config Tenant ID
        APP_CONFIG_TENANT_ID = os.environ['APP_CONFIG_TENANT_ID']

        ## Key Vault Client ID of the App Registration / Service Principal
        APP_CONFIG_CLIENT_ID = os.environ['APP_CONFIG_CLIENT_ID']

        ## Key Vault Client Secret of the App Registration / Service Principal
        APP_CONFIG_CLIENT_SECRET = os.environ['APP_CONFIG_CLIENT_SECRET']
    except:
        APP_CONFIG_NAME = None
        APP_CONFIG_URI = None
        APP_CONFIG_TENANT_ID = None
        APP_CONFIG_CLIENT_ID = None
        APP_CONFIG_CLIENT_SECRET = None

    # Scope for the Power BI REST API call
    # 'https://analysis.windows.net/powerbi/api/App.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Capacity.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Capacity.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/Content.Create',
    # 'https://analysis.windows.net/powerbi/api/Dashboard.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Dashboard.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/Dataflow.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Dataflow.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/Dataset.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Dataset.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/Gateway.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Gateway.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/Pipeline.Deploy',
    # 'https://analysis.windows.net/powerbi/api/Pipeline.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Pipeline.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/Report.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Report.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/StorageAccount.Read.All',
    # 'https://analysis.windows.net/powerbi/api/StorageAccount.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/Tenant.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Tenant.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/UserState.ReadWrite.All',
    # 'https://analysis.windows.net/powerbi/api/Workspace.Read.All',
    # 'https://analysis.windows.net/powerbi/api/Workspace.ReadWrite.All'
    SCOPE = ['https://analysis.windows.net/powerbi/api/.default']

    # Azure AD Login Authority URL
    AUTHORITY = "https://login.microsoftonline.com/" + POWER_BI_TENANT_ID

    # Power BI Base URL 
    PBI_BASE_URL = "https://api.powerbi.com/v1.0/myorg/"
    
    # REST Client Headers
    JSON_HEADERS = {
            "Content-Type": "application/json"
        }
    URL_ENCODED_HEADERS = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    MULTIPART_HEADERS = {
            "Content-Type": "multipart/form-data"
        }
