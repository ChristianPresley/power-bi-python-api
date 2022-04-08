#!/usr/bin/env python

import logging
import datetime
import json
import requests

from typing import List
from urllib import parse

from .rest_client import RestClient
from .workspaces import Workspaces

class Dataflows:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self.workspaces = Workspaces(authz_header, token, token_expiration)
        self._dataflow = {}
        self._dataflow_json = {}
        self._dataflows = None
        
    def get_dataflows(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/dataflows"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self._dataflows = response.json()['value']
            return self._dataflows
        else:
            logging.error("Failed to retrieve pipelines.")
            self.force_raise_http_error(response)
    
    def get_dataflow(self, workspace_name: str, dataflow_name: str) -> List:
        self.client.check_token_expiration()
        self.get_dataflows(workspace_name)

        for item in self._dataflows:
            if item['name'] == dataflow_name:
                self._dataflow = item

        url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/dataflows/" + self._dataflow['objectId']
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self._dataflow_json = json.dumps(response.json(), indent=10)
            return self._dataflow_json
        else:
            logging.error("Failed to retrieve pipelines.")
            self.force_raise_http_error(response)