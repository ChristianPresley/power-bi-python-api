#!/usr/bin/env python

import logging
import requests

from time import sleep

class Users:
    def __init__(self, client):
        self.client = client
        
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/users/refresh-user-permissions
    def refresh_user_access(self, able_wait_time: bool = False) -> bool:
        self.client.check_token_expiration()

        url = self.client.base_url + "RefreshUserPermissions"
        
        response = requests.post(url, headers = self.client.json_headers)
        if able_wait_time:
            sleep(120)
        
        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully refreshed users permission.")
            if not able_wait_time:
                logging.info("Wait for 2 minute recommened before before making other API calls.")
            return True
        else:
            logging.error("Failed to refresh users permission.")
            self.client.force_raise_http_error(response)

    
    