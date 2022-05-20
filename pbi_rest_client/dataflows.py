#!/usr/bin/env python

import logging
import json
import requests
import os

from typing import List
from .utils.utils import Utils
from .workspaces import Workspaces

utils = Utils()

class Dataflows:
    def __init__(self, client):
        self.client = client
        self.workspaces = Workspaces(client)
        self.dataflow = None
        self.dataflow_json = None
        self.dataflows = None
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflow-storage-accounts/get-dataflow-storage-accounts
    def get_dataflow_storage_accounts(self) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "dataflowStorageAccounts/"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self.dataflows = response.json()['value']
            return self.dataflows
        else:
            logging.error("Failed to retrieve pipelines.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/get-dataflows
    def get_dataflows(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/dataflows"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self.dataflows = response.json()['value']
            return self.dataflows
        else:
            logging.error("Failed to retrieve pipelines.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/get-dataflow
    def get_dataflow(self, workspace_name: str, dataflow_name: str) -> List:
        self.client.check_token_expiration()
        self.get_dataflows(workspace_name)
        dataflow_exists = False

        for item in self.dataflows:
            if item['name'] == dataflow_name:
                self.dataflow = item
                dataflow_exists = True
                break
            else:
                self.dataflow = None
                
        if dataflow_exists:
            url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/dataflows/" + self.dataflow['objectId']
        else:
            return logging.info('Dataflow with name: ' + dataflow_name + ' does not exist.')
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self.dataflow_json = json.dumps(response.json(), indent=10)
            return self.dataflow_json
        else:
            logging.error("Failed to retrieve dataflows.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/get-dataflow-data-sources
    def get_dataflow_datasources(self, workspace_name: str, dataflow_name: str) -> List:
        self.client.check_token_expiration()
        self.get_dataflows(workspace_name)
        dataflow_exists = False

        for item in self.dataflows:
            if item['name'] == dataflow_name:
                self.dataflow = item
                dataflow_exists = True
                break
            else:
                self.dataflow = None
                
        if dataflow_exists:
            url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/dataflows/" + self.dataflow['objectId'] + "/datasources"
        else:
            return logging.info('Dataflow with name: ' + dataflow_name + ' does not exist.')
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self.dataflow_json = json.dumps(response.json(), indent=10)
            return self.dataflow_json
        else:
            logging.error("Failed to retrieve dataflows.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/update-dataflow
    def update_dataflow(self, workspace_name: str, dataflow_name: str) -> List:
        self.client.check_token_expiration()
        self.get_dataflow(workspace_name, dataflow_name)
        dataflow_exists = False

        if self.dataflow == None:
            logging.info('Dataflow with name: ' + dataflow_name + " does not exist. Cannot update the dataflow.")
            return None
        if self.dataflow['name'] != dataflow_name:
            logging.info('Dataflow with name: ' + dataflow_name + " does not exist. Cannot update the dataflow.")
            return None
                
        if dataflow_exists:
            self.export_dataflow(workspace_name, dataflow_name)
            url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/dataflows/" + self.dataflow['objectId']
        else:
            return logging.info('Dataflow with name: ' + dataflow_name + ' does not exist.')
        
        payload = {
            "name": "SQLDataFlow",
            "description": "New dataflow description",
            "allowNativeQueries": "false",
            "computeEngineBehavior": "computeOptimized"
        }

        response = requests.patch(url, json = payload, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self.dataflow_json = json.dumps(response.json(), indent=10)
            return self.dataflow_json
        else:
            logging.error("Failed to retrieve dataflows.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/delete-dataflow
    def delete_dataflow(self, workspace_name: str, dataflow_name: str) -> List:
        self.client.check_token_expiration()
        self.get_dataflow(workspace_name, dataflow_name)

        if self.dataflow == None:
            logging.info('Dataflow with name: ' + dataflow_name + " does not exist. Cannot delete the dataflow.")
            return None
        if self.dataflow['name'] != dataflow_name:
            logging.info('Dataflow with name: ' + dataflow_name + " does not exist. Cannot delete the dataflow.")
            return None
        
        self.export_dataflow(workspace_name, dataflow_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/dataflows/" + self.dataflow['objectId']
        
        response = requests.delete(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            self.dataflow = None
            return logging.info("Successfully deleted dataflow with name: " + dataflow_name + " in workspace: " + workspace_name)
        else:
            logging.error("Failed to delete dataflow with name: " + dataflow_name + " in workspace: " + workspace_name)
            self.client.force_raise_http_error(response)

    def export_dataflow(self, workspace_name: str, dataflow_name: str):
        self.client.check_token_expiration()
        self.get_dataflow(workspace_name, dataflow_name)

        out_file = dataflow_name + ".json"
        blob = utils.blob_client(out_file)

        with open(out_file, "w+") as f:
                f.write(self.dataflow_json)
        with open(out_file, "rb") as data:
            blob.upload_blob(data, overwrite = True)