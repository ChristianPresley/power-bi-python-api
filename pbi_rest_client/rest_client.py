#!/usr/bin/env python

import sys
import os
import datetime
import logging
import requests

from typing import Dict, List, NoReturn, Union
from msal import PublicClientApplication

class RestClient:
    tenant_id = os.getenv('AZURE_TENANT_ID')
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
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

    base_url = "https://api.powerbi.com/v1.0/myorg/"
    json_headers = {"Content-Type": "application/json"}
    urlencoded_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    multipart_headers = {"Content-Type": "multipart/form-data"}

    http_accepted_code = 202
    http_created_code = 201
    http_ok_code = 200
    
    def __init__(self, authz_header = None, token = None, token_expiration = None):
            self.tenant_id = RestClient.tenant_id
            self.client_id = RestClient.client_id
            self.base_url = RestClient.base_url
            self.http_accepted_code = RestClient.http_accepted_code
            self.http_created_code = RestClient.http_created_code
            self.http_ok_code = RestClient.http_ok_code
            self.authz_header = authz_header
            self.token = token
            self.token_expiration = token_expiration
            self.request_bearer_token()
            self.json_headers = RestClient.json_headers
            self.json_headers.update(self.authz_header)
            self.urlencoded_headers = RestClient.urlencoded_headers
            self.urlencoded_headers.update(self.authz_header)
            self.multipart_headers = RestClient.multipart_headers
            self.multipart_headers.update(self.authz_header)
            self._workspaces = None
            self._pipelines = None

    def get_authz_header(self) -> Dict[str, str]:
        return {"Authorization": "Bearer " + self.token}
    
    def request_bearer_token(self) -> None:
        renew_token = True

        if self.token is None:
            logging.info(f"Access token does not exist. Attempting to generate access token.")    
        elif self.token_expiration < datetime.datetime.utcnow():
            logging.info(f"Access token has expired. Attempting to renew access token.")
        else:
            logging.info("Access token exists and is not expired. Proceeding to use existing token.")
            renew_token = False

        if renew_token:
            app = PublicClientApplication(
                client_id = self.client_id,
                authority = "https://login.microsoftonline.com/" + self.tenant_id
            )

            acquire_tokens_result = app.acquire_token_by_username_password(
                username = RestClient.username,
                password = RestClient.password,
                scopes = RestClient.scope
            )

            if 'error' in acquire_tokens_result:
                logging.error(f"Failed to retrieve access token for client id {self.client_id}.")
                logging.error("Error: " + acquire_tokens_result['error'])
                raise Exception("Description: " + acquire_tokens_result['error_description'])
            else:
                logging.info(f"Successfully retrieved access token for client id {self.client_id}.")
                self.token = acquire_tokens_result['access_token']
                self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=acquire_tokens_result["expires_in"])
                self.authz_header = self.get_authz_header()
    
    def check_token_expiration(self):
        if self.token_expiration < datetime.datetime.utcnow():
            self.request_bearer_token()

    def force_raise_http_error(response: int):
        logging.error("Expected response code(s) {expected_codes}, got {response.status_code}: {response.text}.")
        response.raise_for_status()
        raise requests.HTTPError(response)
    