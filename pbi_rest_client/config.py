#!/usr/bin/env python

import os

from pbi_rest_client.utils.utils import Utils

utils = Utils()

class BaseConfig(object):
    # 'ServiceAccount' or 'ServicePrincipal'
    auth_mode = utils.auth_mode
    if auth_mode:
        AUTHENTICATION_MODE = 'ServiceAccount'
        SERVICE_ACCOUNT_USERNAME = os.getenv('AZURE_USERNAME')
        SERVICE_ACCOUNT_PASSWORD = os.getenv('AZURE_PASSWORD')
    elif not auth_mode:
        AUTHENTICATION_MODE = 'ServicePrincipal'
        SERVICE_ACCOUNT_USERNAME = None
        SERVICE_ACCOUNT_PASSWORD = None
    
    # Azure Tenant ID for authentication
    TENANT_ID = os.getenv('AZURE_TENANT_ID')

    # Client ID of the App Registration / Service Principal
    CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
    
    # Client secret of the App Registration / Service Principal
    # Only required for ServicePrincipal
    CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

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
    AUTHORITY = "https://login.microsoftonline.com/" + TENANT_ID

    # Power BI Base URL
    PBI_BASE_URL = "https://api.powerbi.com/v1.0/myorg/"
    