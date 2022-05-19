#!/usr/bin/env python

import logging
import requests

from typing import List
from .rest_client import RestClient
from .workspaces import Workspaces

class Dashboards:
    def __init__(self, client):
        self.client = client
        # self.workspaces = Workspaces(authz_header, token, token_expiration)
        self.workspaces = Workspaces(client)
        self.dashboards = []

    # https://docs.microsoft.com/en-us/rest/api/power-bi/dashboards/get-dashboards-in-group
    def get_dashboards(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/dashboards"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            for item in response.json()['value']:
                self.dashboards.append(item)
            return self.dashboards
        else:
            logging.error("Failed to retrieve dashboard.")
            self.client.force_raise_http_error(response)
    