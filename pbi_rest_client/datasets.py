#!/usr/bin/env python

import logging
import json
import requests

from typing import List
from .workspaces import Workspaces

class Datasets:
    def __init__(self, client):
        self.client = client
        self.workspaces = Workspaces(client)
        self.dataset = {}
        self.dataset_parameters = {}
        self.dataset_json = {}
        self.datasets = None

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset
    def get_dataset(self, workspace_name: str) -> List:
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
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasets
    def get_datasets(self) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "datasets"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspaces.")
            self.datasets = response.json()["value"]
            return self.datasets
        else:
            logging.error("Failed to retrieve workspaces.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasets
    def bind_to_gateway(self, workspace_name) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/8e677ee5-5423-4ab4-8c33-3cd4161790af/Default.BindToGateway"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspaces.")
            self.datasets = response.json()["value"]
            return self.datasets
        else:
            logging.error("Failed to retrieve workspaces.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasets-in-group
    def get_datasets_in_workspace(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspaces.")
            self.datasets = response.json()["value"]
            return self.datasets
        else:
            logging.error("Failed to retrieve workspaces.")
            self.client.force_raise_http_error(response)

    def get_dataset_id(self, dataset_name: str) -> str:
        self.client.check_token_expiration()
        self.get_datasets()
        dataset_missing = True

        for item in self.datasets:
            if item['name'] == dataset_name:
                logging.info(f"Found workspace with name {dataset_name} and workspace id {item['id']}.")
                self.dataset = {dataset_name: item['id']}
                dataset_missing = False
                return self.dataset
        if dataset_missing:
            logging.warning(f"Unable to find workspace with name: '{dataset_name}'")

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset-in-group
    def get_dataset_in_workspace_id(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_datasets_in_workspace(workspace_name)
        dataset_missing = True

        for item in self.datasets:
            if item['name'] == dataset_name:
                logging.info(f"Found workspace with name {dataset_name} and workspace id {item['id']}.")
                self.dataset = {dataset_name: item['id']}
                dataset_missing = False
                return self.dataset
        if dataset_missing:
            logging.warning(f"Unable to find workspace with name: '{dataset_name}'")

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-parameters
    def get_dataset_parameters(self, dataset_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_id(dataset_name)

        url = self.client.base_url + "datasets/" + self.dataset[dataset_name] + "/parameters"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspaces.")
            self.dataset_parameters = response.json()
            return self.dataset_parameters
        else:
            logging.error("Failed to retrieve workspaces.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-parameters-in-group
    def get_dataset_in_group_parameters(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/parameters"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspaces.")
            self.dataset_parameters = response.content
            return self.dataset_parameters
        else:
            logging.error("Failed to retrieve workspaces.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasources-in-group
    def get_datasources(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/datasources"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspaces.")
            self.dataset_parameters = response.content
            return self.dataset_parameters
        else:
            logging.error("Failed to retrieve workspaces.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/take-over-in-group
    def take_dataset_owner(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/c8aaf294-e7d3-4ed2-964a-df19bcec5455/Default.TakeOver"
        
        response = requests.post(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self.dataflow_json = json.dumps(response.json(), indent=10)
            return self.dataflow_json
        else:
            logging.error("Failed to retrieve pipelines.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/refresh-dataset-in-group
    def refresh_dataset(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/c8aaf294-e7d3-4ed2-964a-df19bcec5455/Default.TakeOver"
        
        response = requests.post(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved dataflows.")
            self.dataflow_json = json.dumps(response.json(), indent=10)
            return self.dataflow_json
        else:
            logging.error("Failed to retrieve pipelines.")
            self.client.force_raise_http_error(response)