#!/usr/bin/env python

import logging
import requests

from datetime import datetime, timedelta
from msal import PublicClientApplication, ConfidentialClientApplication
from .config import BaseConfig

config = BaseConfig()

# Variables
http_ok_code = 200
http_created_code = 201
http_accepted_code = 202
expected_codes = [http_ok_code, http_created_code, http_accepted_code]

class RestClient:
    def __init__(self):
        self.app = None
        self.token = None
        self.base_url = config.PBI_BASE_URL
        self.http_ok_code = http_ok_code
        self.http_created_code = http_created_code
        self.http_accepted_code = http_accepted_code
        self.expected_codes = expected_codes
        self.authz_header = {"Authorization": self.token}
        self.token_expiration = datetime.today() - timedelta(days = 1)
        self.check_token_expiration()
        self.json_headers = config.JSON_HEADERS
        self.json_headers.update(self.authz_header)
        self.url_encoded_headers = config.URL_ENCODED_HEADERS
        self.url_encoded_headers.update(self.authz_header)
        self.multipart_headers = config.MULTIPART_HEADERS
        self.multipart_headers.update(self.authz_header)

    def request_bearer_token(self) -> None:
        if self.app == None:
            if config.AUTHENTICATION_MODE == 'ServiceAccount':
                logging.info('Authentication mode set to: ' + config.AUTHENTICATION_MODE)

                # https://msal-python.readthedocs.io/en/latest/#publicclientapplication
                self.app = PublicClientApplication(
                    client_id = config.CLIENT_ID,
                    authority = config.AUTHORITY
                )
            elif config.AUTHENTICATION_MODE == 'ServicePrincipal':
                logging.info('Authentication mode set to: ' + config.AUTHENTICATION_MODE)

                # https://msal-python.readthedocs.io/en/latest/#confidentialclientapplication
                self.app = ConfidentialClientApplication(
                    client_id = config.CLIENT_ID,
                    client_credential = config.CLIENT_SECRET,
                    authority = config.AUTHORITY
                )
            else:
                raise Exception("Invalid authentication mode specified. Must be 'ServiceAccount' or 'ServicePrincipal'")
        
        if self.token is None:
            logging.info("Access token does not exist. Attempting to generate access token.")

            if isinstance(self.app, PublicClientApplication):
                # https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_by_username_password
                acquire_tokens_result = self.app.acquire_token_by_username_password(
                    username = config.SERVICE_ACCOUNT_USERNAME,
                    password = config.SERVICE_ACCOUNT_PASSWORD,
                    scopes = config.SCOPE
                )

                self.account_username = acquire_tokens_result['id_token_claims']['preferred_username']
            elif isinstance(self.app, ConfidentialClientApplication):
                # https://msal-python.readthedocs.io/en/latest/#msal.ConfidentialClientApplication.acquire_token_for_client
                acquire_tokens_result = self.app.acquire_token_for_client(
                    scopes = config.SCOPE
                )
        elif self.token_expiration < datetime.utcnow():
            logging.info("Access token has expired. Attempting to renew access token.")

            if isinstance(self.app, PublicClientApplication):
                # https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_silent_with_error
                acquire_tokens_result = self.app.acquire_token_silent_with_error(scopes = config.SCOPE, account = self.app.get_accounts(self.account_username)[0])
            elif isinstance(self.app, ConfidentialClientApplication):
                # https://msal-python.readthedocs.io/en/latest/#msal.ConfidentialClientApplication.acquire_token_silent_with_error
                acquire_tokens_result = self.app.acquire_token_silent_with_error(scopes = config.SCOPE, account = None)

        if 'error' in acquire_tokens_result:
            logging.error(f"Failed to retrieve access token for client id {config.CLIENT_ID}.")
            logging.error("Error: " + acquire_tokens_result['error'])
            raise Exception("Description: " + acquire_tokens_result['error_description'])
        else:
            logging.info(f"Successfully retrieved access token for client id {config.CLIENT_ID}.")
            self.token = acquire_tokens_result['access_token']
            self.token_expiration = datetime.utcnow() + timedelta(seconds=acquire_tokens_result["expires_in"])
            self.authz_header = {"Authorization": "Bearer " + self.token}
    
    def check_token_expiration(self):
        if self.token_expiration < datetime.utcnow():
            self.request_bearer_token()
        else:
            logging.debug("Access token exists and is not expired. Proceeding to use existing token.")

    def force_raise_http_error(self, response: int):
        logging.error(f"Expected response codes: {self.expected_codes}, response was: {response.status_code}: {response.text}.")
        response.raise_for_status()
        raise requests.HTTPError(response)
    