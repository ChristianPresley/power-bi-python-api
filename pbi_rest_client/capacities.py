#!/usr/bin/env python

import logging
import requests

from typing import List
from urllib import parse

from .rest_client import RestClient
from .workspaces import Workspaces

class Capacities:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self.workspaces = Workspaces(authz_header, token, token_expiration)
        self._workspaces = self.workspaces.get_workspaces()

    def set_workspace_capacity(self, workspace_name: str, capacity: str) -> None:
        self.client.check_token_expiration()

        self.workspaces.get_workspace_id(workspace_name)

        for item in self._workspaces:
            if item['id'] == self.workspaces._workspace[workspace_name] and 'capacityId' in item:
                if item['capacityId'] == capacity:
                    logging.info(f"Workspace with id: {item['id']} is already assigned to capacity {capacity}.")
                    return item
                if item['capacityId'] != capacity:
                    logging.warning(f"Workspace with id: {item['id']} is assigned to the wrong capacity with id {item['capacityId']}. "
                    + f"Proceeding to assign capacity with id {capacity}.")
                    break
            elif item['id'] == self.workspaces._workspace[workspace_name] and 'capacityId' not in item:
                logging.info(f"Workspace with id: {item['id']} is not assigned to capacity. Proceeding to assign capacity with id {capacity}.")
                break

        url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/AssignToCapacity"

        payload = {
            "capacityId": capacity
        }

        response = requests.post(url, data = payload, headers = self.client.urlencoded_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully changed capacity of workspace {workspace_name} to {capacity}.")
            return response
        else:
            logging.error(f"Failed to change capacity of workspace {workspace_name} to {capacity}.")
            self.force_raise_http_error(response)