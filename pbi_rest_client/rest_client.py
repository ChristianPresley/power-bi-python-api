#!/usr/bin/env python

import logging
import requests

from datetime import datetime, timedelta
from msal import PublicClientApplication, ConfidentialClientApplication
from .config import BaseConfig
from azure.identity import InteractiveBrowserCredential


config = BaseConfig()

class RestClient:
    def __init__(self):
        self.app = None
        self.token = None
        self.account_username = None
        self.log_with_personal_account = config.LOG_WITH_PERSONAL_ACCOUNT #Adding to enable authentication via browser
        self.base_url = config.PBI_BASE_URL
        self.http_ok_code = 200
        self.http_created_code = 201
        self.http_accepted_code = 202
        self.expected_codes = [self.http_ok_code, self.http_created_code, self.http_accepted_code]
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
            if config.LOG_WITH_PERSONAL_ACCOUNT:
                logging.info('Authentication via browser using email address.')

                # https://www.datalineo.com/post/power-bi-rest-api-with-python-part-iii-azure-identity
                self.app = InteractiveBrowserCredential()

            elif config.AUTHENTICATION_MODE == 'ServiceAccount':
                logging.info('Authentication mode set to: ' + config.AUTHENTICATION_MODE)

                # https://msal-python.readthedocs.io/en/latest/#publicclientapplication
                self.app = PublicClientApplication(
                    client_id = config.POWER_BI_CLIENT_ID,
                    authority = config.AUTHORITY
                )
            elif config.AUTHENTICATION_MODE == 'ServicePrincipal':
                logging.info('Authentication mode set to: ' + config.AUTHENTICATION_MODE)

                # https://msal-python.readthedocs.io/en/latest/#confidentialclientapplication
                self.app = ConfidentialClientApplication(
                    client_id = config.POWER_BI_CLIENT_ID,
                    client_credential = config.POWER_BI_CLIENT_SECRET,
                    authority = config.AUTHORITY
                )
            else:
                raise Exception("Invalid authentication mode specified. Must be 'ServiceAccount' or 'ServicePrincipal'")
        
        if self.token is None:
            logging.info("Access token does not exist. Attempting to generate access token.")

            if isinstance(self.app, InteractiveBrowserCredential):
                # https://www.datalineo.com/post/power-bi-rest-api-with-python-part-iii-azure-identity
                try:
                    acquire_tokens_result = self.app.get_token(config.SCOPE.pop() )
                except Exception as e:
                    acquire_tokens_result = {'error': 'Error on getting token', 'error_description': getattr(e, 'message', repr(e))}

            elif isinstance(self.app, PublicClientApplication):
                # https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_by_username_password
                acquire_tokens_result = self.app.acquire_token_by_username_password(
                    username = config.SERVICE_ACCOUNT_USERNAME,
                    password = config.SERVICE_ACCOUNT_PASSWORD,
                    scopes = config.SCOPE
                )
            elif isinstance(self.app, ConfidentialClientApplication):
                # https://msal-python.readthedocs.io/en/latest/#msal.ConfidentialClientApplication.acquire_token_for_client
                acquire_tokens_result = self.app.acquire_token_for_client(
                    scopes = config.SCOPE
                )
        elif self.token_expiration < datetime.utcnow():
            logging.info("Access token has expired. Attempting to renew access token.")

            if isinstance(self.app, InteractiveBrowserCredential):
                try:
                    acquire_tokens_result = self.app.get_token(config.SCOPE.pop() )
                except Exception as e:
                    acquire_tokens_result = {'error': 'Error on getting token', 'error_description': getattr(e, 'message', repr(e))}
            elif isinstance(self.app, PublicClientApplication):
                # https://msal-python.readthedocs.io/en/latest/#msal.PublicClientApplication.acquire_token_silent_with_error
                acquire_tokens_result = self.app.acquire_token_silent_with_error(scopes = config.SCOPE, account = self.app.get_accounts(self.account_username)[0])
            elif isinstance(self.app, ConfidentialClientApplication):
                # https://msal-python.readthedocs.io/en/latest/#msal.ConfidentialClientApplication.acquire_token_silent_with_error
                acquire_tokens_result = self.app.acquire_token_silent_with_error(scopes = config.SCOPE, account = None)

        if 'error' in acquire_tokens_result:
            if isinstance(self.app, InteractiveBrowserCredential):
                logging.error("Failed to retrieve access token via browser.")
            else:
                logging.error(f"Failed to retrieve access token for client id {config.POWER_BI_CLIENT_ID}.")
            logging.error("Error: " + acquire_tokens_result['error'])
            raise Exception("Description: " + acquire_tokens_result['error_description'])
        else:
            if isinstance(self.app, InteractiveBrowserCredential):
                logging.info(f"Successfully retrieved access token via browser.")
                self.token = acquire_tokens_result.token
                utc_offset = datetime.utcnow() - datetime.now()
                self.token_expiration = datetime.fromtimestamp(acquire_tokens_result.expires_on) + utc_offset
            else:
                logging.info(f"Successfully retrieved access token for client id {config.POWER_BI_CLIENT_ID}.")
                if isinstance(self.app, PublicClientApplication):
                    self.account_username = acquire_tokens_result['id_token_claims']['preferred_username']
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
    