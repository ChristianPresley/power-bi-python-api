#!/usr/bin/env python

import logging
import json
import requests
import os

from typing import List
from azure.storage.blob import BlobClient
from .rest_client import RestClient
from .workspaces import Workspaces

class Dataflows:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self.workspaces = Workspaces(authz_header, token, token_expiration)
        self._dataflow = None
        self._dataflow_json = None
        self._dataflows = None
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflow-storage-accounts/get-dataflow-storage-accounts
    def get_dataflow_storage_accounts(self) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "dataflowStorageAccounts/"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self._dataflows = response.json()['value']
            return self._dataflows
        else:
            logging.error("Failed to retrieve pipelines.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/get-dataflows
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
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/get-dataflow
    def get_dataflow(self, workspace_name: str, dataflow_name: str, blob_container_name: str) -> List:
        self.client.check_token_expiration()
        self.get_dataflows(workspace_name)
        dataflow_exists = False

        for item in self._dataflows:
            if item['name'] == dataflow_name:
                self._dataflow = item
                dataflow_exists = True
                break
            else:
                self._dataflow = None
                
        if dataflow_exists:
            blob = BlobClient.from_connection_string(conn_str=os.getenv('AZURE_STORAGE_CONNECTION_STRING'), container_name=blob_container_name, blob_name=f"{self._dataflow}")
            url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/dataflows/" + self._dataflow['objectId']
        else:
            return logging.info('Dataflow with name: ' + dataflow_name + ' does not exist.')
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self._dataflow_json = json.dumps(response.json(), indent=10)
            with open("test.json", "w+") as f:
                f.write(self._dataflow_json)
            with open("test.json", "rb") as data:
                blob.upload_blob(data, overwrite = True)
            return self._dataflow_json
        else:
            logging.error("Failed to retrieve dataflows.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/get-dataflow-data-sources
    def get_dataflow_datasources(self, workspace_name: str, dataflow_name: str) -> List:
        self.client.check_token_expiration()
        self.get_dataflows(workspace_name)
        dataflow_exists = False

        for item in self._dataflows:
            if item['name'] == dataflow_name:
                self._dataflow = item
                dataflow_exists = True
                break
            else:
                self._dataflow = None
                
        if dataflow_exists:
            blob = BlobClient.from_connection_string(conn_str=os.getenv('AZURE_STORAGE_CONNECTION_STRING'), container_name="test-container", blob_name=f"{self._dataflow}")
            url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/dataflows/" + self._dataflow['objectId'] + "/datasources"
        else:
            return logging.info('Dataflow with name: ' + dataflow_name + ' does not exist.')
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self._dataflow_json = json.dumps(response.json(), indent=10)
            with open("test.json", "w+") as f:
                f.write(self._dataflow_json)
            with open("test.json", "rb") as data:
                blob.upload_blob(data, overwrite = True)
            return self._dataflow_json
        else:
            logging.error("Failed to retrieve dataflows.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/update-dataflow
    def update_dataflow(self, workspace_name: str, dataflow_name: str) -> List:
        self.client.check_token_expiration()
        self.get_dataflows(workspace_name)
        dataflow_exists = False

        for item in self._dataflows:
            if item['name'] == dataflow_name:
                self._dataflow = item
                dataflow_exists = True
                break
            else:
                self._dataflow = None
                
        if dataflow_exists:
            blob = BlobClient.from_connection_string(conn_str=os.getenv('AZURE_STORAGE_CONNECTION_STRING'), container_name="test-container", blob_name=f"{self._dataflow}")
            url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/dataflows/" + self._dataflow['objectId']
        else:
            return logging.info('Dataflow with name: ' + dataflow_name + ' does not exist.')
        
        payload = {
            "name": "SQLDataFlow",
            "description": "New dataflow description",
            "allowNativeQueries": "false",
            "computeEngineBehavior": "computeOptimized",
            "datasourceType": "Sql",
            "connectionDetails": {
                "server": "df6bce77.database.windows.net",
                "database": "kpdemo"
            },
            "datasourceId": "8e677ee5-5423-4ab4-8c33-3cd4161790af",
            "gatewayId": "c56e344f-a21f-4913-8e85-92e86a12903f",
        }

        response = requests.patch(url, json = payload, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self._dataflow_json = json.dumps(response.json(), indent=10)
            with open("test.json", "w+") as f:
                f.write(self._dataflow_json)
            with open("test.json", "rb") as data:
                blob.upload_blob(data, overwrite = True)
            return self._dataflow_json
        else:
            logging.error("Failed to retrieve dataflows.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/dataflows/delete-dataflow
    def delete_dataflow(self, workspace_name: str, dataflow_name: str) -> List:
        self.client.check_token_expiration()
        self.get_dataflow(workspace_name, dataflow_name)

        if self._dataflow == None:
            logging.info('Dataflow with name: ' + dataflow_name + " does not exist. Cannot delete the dataflow.")
            return None
        if self._dataflow['name'] != dataflow_name:
            logging.info('Dataflow with name: ' + dataflow_name + " does not exist. Cannot delete the dataflow.")
            return None

        url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/dataflows/" + self._dataflow['objectId']
        
        response = requests.delete(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            self._dataflow = None
            return logging.info("Successfully deleted dataflow with name: " + dataflow_name + " in workspace: " + workspace_name)
        else:
            logging.error("Failed to delete dataflow with name: " + dataflow_name + " in workspace: " + workspace_name)
            self.client.force_raise_http_error(response)
