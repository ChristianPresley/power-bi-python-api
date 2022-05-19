#!/usr/bin/env python

import logging
import requests

from typing import List
from .rest_client import RestClient

class Workspaces:
    # def __init__(self, authz_header = None, token = None, token_expiration = None):
    #     self.client = RestClient(authz_header, token, token_expiration)
    #     self._workspaces = None
    #     self._workspace = {}

    def __init__(self):
        self.client = RestClient()
        self._workspaces = None
        self._workspace = {}
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/get-groups
    def get_workspace(self, workspace_name: str) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "groups?$filter=" + "name eq '" + workspace_name + "'"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            if response.json()["@odata.count"] <= 0:
                logging.info("Workspace does not exist or user does not have permissions.")
                return None
            elif response.json()["@odata.count"] == 1:
                logging.info("Successfully retrieved workspace.")
                return response.json()
        else:
            logging.error("Failed to retrieve workspace.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/get-groups
    def get_workspaces(self) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "groups"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspaces.")
            self._workspaces = response.json()["value"]
            return self._workspaces
        else:
            logging.error("Failed to retrieve workspaces.")
            self.client.force_raise_http_error(response)

    def get_workspace_id(self, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_workspaces()
        workspace_missing = True

        for item in self._workspaces:
            if item['name'] == workspace_name:
                logging.info(f"Found workspace with name {workspace_name} and workspace id {item['id']}.")
                self._workspace = {workspace_name: item['id']}
                workspace_missing = False
                return self._workspace
        if workspace_missing:
            logging.warning(f"Unable to find workspace with name: '{workspace_name}'")
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/create-group
    def create_workspace(self, workspace_name: str) -> None:
        self.client.check_token_expiration()

        workspace = self.get_workspace(workspace_name)
                
        if workspace != None:
            logging.info(f"The workspace {workspace_name} already exists, no changes made.")
            return workspace["value"]

        logging.info(f"Trying to create workspace with name: {workspace_name}...")

        url = self.client.base_url + "groups?workspaceV2=True"

        payload = {
            "name": workspace_name
        }
        
        response = requests.post(url, data = payload, headers = self.client.url_encoded_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully created workspace {workspace_name}.")
            self.get_workspaces()
            return response.json()
        else:
            logging.error(f"Failed to create workspace {workspace_name}.")
            self.client.force_raise_http_error(response)
