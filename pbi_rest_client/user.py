from msal import PublicClientApplication
import sys
import os

tenant_id = os.getenv('AZURE_TENANT_ID')
client_id = os.getenv('AZURE_CLIENT_ID')
username = os.getenv('AZURE_USERNAME')
password = os.getenv('AZURE_PASSWORD')

scope = [
    'https://analysis.windows.net/powerbi/api/App.Read.All',
    'https://analysis.windows.net/powerbi/api/Capacity.Read.All',
    'https://analysis.windows.net/powerbi/api/Capacity.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/Content.Create',
    'https://analysis.windows.net/powerbi/api/Dashboard.Read.All',
    'https://analysis.windows.net/powerbi/api/Dashboard.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/Dataflow.Read.All',
    'https://analysis.windows.net/powerbi/api/Dataflow.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/Dataset.Read.All',
    'https://analysis.windows.net/powerbi/api/Dataset.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/Gateway.Read.All',
    'https://analysis.windows.net/powerbi/api/Gateway.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/Pipeline.Deploy',
    'https://analysis.windows.net/powerbi/api/Pipeline.Read.All',
    'https://analysis.windows.net/powerbi/api/Pipeline.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/Report.Read.All',
    'https://analysis.windows.net/powerbi/api/Report.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/StorageAccount.Read.All',
    'https://analysis.windows.net/powerbi/api/StorageAccount.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/Tenant.Read.All',
    'https://analysis.windows.net/powerbi/api/Tenant.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/UserState.ReadWrite.All',
    'https://analysis.windows.net/powerbi/api/Workspace.Read.All',
    'https://analysis.windows.net/powerbi/api/Workspace.ReadWrite.All'
]

if (len(sys.argv) > 1) and (len(sys.argv) != 5):
  print("Usage: get-tokens-for-user.py <client ID> <tenant ID> <username> <password>")
  exit(1)

if len(sys.argv) > 1:
  client_id = sys.argv[1]
  tenant_id = sys.argv[2]
  username = sys.argv[3]
  password = sys.argv[4]

app = PublicClientApplication(
  client_id = client_id,
  authority = "https://login.microsoftonline.com/" + tenant_id
)

acquire_tokens_result = app.acquire_token_by_username_password(
  username = username,
  password = password,
  scopes = scope
)

if 'error' in acquire_tokens_result:
  print("Error: " + acquire_tokens_result['error'])
  print("Description: " + acquire_tokens_result['error_description'])
else:
  print("Access token:\n")
  print(acquire_tokens_result['access_token'])
  print("\nRefresh token:\n")
  print(acquire_tokens_result['refresh_token'])