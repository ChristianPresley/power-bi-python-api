#!/usr/bin/env python

import logging
import requests

from .rest_client import RestClient
from .workspaces import Workspaces

class Capacities:
    def __init__(self, client):
        self.client = client
        self.workspaces = Workspaces(client)
        self.workspaces = self.workspaces.get_workspaces()

    # https://docs.microsoft.com/en-us/rest/api/power-bi/capacities/groups-assign-to-capacity
    def set_workspace_capacity(self, workspace_name: str, capacity: str) -> None:
        self.client.check_token_expiration()

        self.workspaces.get_workspace_id(workspace_name)

        for item in self.workspaces:
            if item['id'] == self.workspaces.workspace[workspace_name] and 'capacityId' in item:
                if item['capacityId'] == capacity:
                    logging.info(f"Workspace with id: {item['id']} is already assigned to capacity {capacity}.")
                    return item
                if item['capacityId'] != capacity:
                    logging.warning(f"Workspace with id: {item['id']} is assigned to the wrong capacity with id {item['capacityId']}. "
                    + f"Proceeding to assign capacity with id {capacity}.")
                    break
            elif item['id'] == self.workspaces.workspace[workspace_name] and 'capacityId' not in item:
                logging.info(f"Workspace with id: {item['id']} is not assigned to capacity. Proceeding to assign capacity with id {capacity}.")
                break

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/AssignToCapacity"

        payload = {
            "capacityId": capacity
        }

        response = requests.post(url, data = payload, headers = self.client.url_encoded_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully changed capacity of workspace {workspace_name} to {capacity}.")
            return response
        else:
            logging.error(f"Failed to change capacity of workspace {workspace_name} to {capacity}.")
            self.client.force_raise_http_error(response)