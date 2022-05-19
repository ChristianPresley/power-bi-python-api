#!/usr/bin/env python

import datetime
import logging
import requests

from typing import Dict
from msal import PublicClientApplication, ConfidentialClientApplication
from .config import BaseConfig

config = BaseConfig()

class RestClient:
    json_headers = {"Content-Type": "application/json"}
    urlencoded_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    multipart_headers = {"Content-Type": "multipart/form-data"}

    http_ok_code = 200
    http_created_code = 201
    http_accepted_code = 202
    expected_codes = [http_ok_code, http_created_code, http_accepted_code]
    
    def __init__(self, authz_header = None, token = None, token_expiration = None):
            self.base_url = config.PBI_BASE_URL
            self.http_ok_code = RestClient.http_ok_code
            self.http_created_code = RestClient.http_created_code
            self.http_accepted_code = RestClient.http_accepted_code
            self.expected_codes = RestClient.expected_codes
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
            if config.AUTHENTICATION_MODE == 'ServiceAccount':
                logging.info('Authentication mode set to: ' + config.AUTHENTICATION_MODE)

                # https://msal-python.readthedocs.io/en/latest/#publicclientapplication
                app = PublicClientApplication(
                    client_id = config.CLIENT_ID,
                    authority = config.AUTHORITY
                )

                # https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_by_username_password
                acquire_tokens_result = app.acquire_token_by_username_password(
                    username = config.SERVICE_ACCOUNT_USERNAME,
                    password = config.SERVICE_ACCOUNT_PASSWORD,
                    scopes = config.SCOPE
                )
            elif config.AUTHENTICATION_MODE == 'ServicePrincipal':
                logging.info('Authentication mode set to: ' + config.AUTHENTICATION_MODE)

                # https://msal-python.readthedocs.io/en/latest/#confidentialclientapplication
                app = ConfidentialClientApplication(
                    client_id = config.CLIENT_ID,
                    client_credential = config.CLIENT_SECRET,
                    authority = config.AUTHORITY
                )

                # https://msal-python.readthedocs.io/en/latest/#msal.ConfidentialClientApplication.acquire_token_for_client
                acquire_tokens_result = app.acquire_token_for_client(
                    scopes = config.SCOPE
                )
            else:
                raise Exception("Invalid authentication mode specified. Must be 'ServiceAccount' or 'ServicePrincipal'")

            if 'error' in acquire_tokens_result:
                logging.error(f"Failed to retrieve access token for client id {config.CLIENT_ID}.")
                logging.error("Error: " + acquire_tokens_result['error'])
                raise Exception("Description: " + acquire_tokens_result['error_description'])
            else:
                logging.info(f"Successfully retrieved access token for client id {config.CLIENT_ID}.")
                self.token = acquire_tokens_result['access_token']
                self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=acquire_tokens_result["expires_in"])
                self.authz_header = self.get_authz_header()
    
    def check_token_expiration(self):
        if self.token_expiration < datetime.datetime.utcnow():
            self.request_bearer_token()

    def force_raise_http_error(self, response: int):
        logging.error(f"Expected response codes: {self.expected_codes}, response was: {response.status_code}: {response.text}.")
        response.raise_for_status()
        raise requests.HTTPError(response)
    