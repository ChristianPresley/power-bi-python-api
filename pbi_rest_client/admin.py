#!/usr/bin/env python

import logging
import datetime
import requests

from typing import List
from urllib import parse

from .rest_client import RestClient

class Admin:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self._workspaces = None
        self._workspace = {}

    # https://docs.microsoft.com/en-us/rest/api/power-bi/admin/groups-get-groups-as-admin
    def get_workspaces(self) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "admin/groups"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspaces.")
            self._workspaces = response.json()["value"]
            return self._workspaces
        else:
            logging.error("Failed to retrieve workspaces.")
            print(response.status_code)
            self.client.force_raise_http_error(response.status_code)
