#!/usr/bin/env python

import logging
import datetime
import json
import requests

from typing import List
from urllib import parse

from .rest_client import RestClient
from .workspaces import Workspaces

class Datasets:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self.workspaces = Workspaces(authz_header, token, token_expiration)
        self._dataset = {}
        self._dataset_json = {}
        self._datasets = None
    
    def take_dataset_owner(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/datasets/c8aaf294-e7d3-4ed2-964a-df19bcec5455/Default.TakeOver"
        
        response = requests.post(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self._dataflow_json = json.dumps(response.json(), indent=10)
            return self._dataflow_json
        else:
            logging.error("Failed to retrieve pipelines.")
            self.force_raise_http_error(response)