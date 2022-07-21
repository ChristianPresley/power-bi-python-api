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
        self.dataset_refreshes = None
        self.dataset_refresh = {}
        self.dataset_datasources = None
        self.dataset_refresh_details = None
        self.dataset_refresh_schedule = None

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset
    # Get specific dataset from My Workspace
    def get_dataset(self, dataset_id: str) -> str:
        self.client.check_token_expiration()

        url = self.client.base_url + "datasets" + dataset_id
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            if response.json()["@odata.count"] <= 0:
                logging.info("Dataset does not exist or user does not have permissions.")
                return None
            elif response.json()["@odata.count"] == 1:
                logging.info("Successfully retrieved dataset.")
                return response.json()
        else:
            logging.error("Failed to retrieve dataset.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasets
    # Get all Datasets from My Workspace
    def get_datasets(self) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "datasets"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved datasets from My workspace.")
            self.datasets = response.json()["value"]
            return self.datasets
        else:
            logging.error("Failed to retrieve datasets My workspace.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/bind-to-gateway
    def bind_to_gateway(self, workspace_name: str, dataset_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset +"/Default.BindToGateway"
        
        response = requests.post(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(F"Successfully binding dataset {dataset_name} in workspace {workspace_name} to gateway.")
            self.dataset_json = json.dumps(response.json(), indent=10)
            return self.dataset_json
        else:
            logging.error(f"Failed to bind dataset {dataset_name} in workspace {workspace_name} to gateway.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasets-in-group
    def get_datasets_in_workspace(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved datasets.")
            self.datasets = response.json()["value"]
            return self.datasets
        else:
            logging.error("Failed to retrieve datasets.")
            self.client.force_raise_http_error(response)

    # Get Dataset id from dataset_name in My Workspace
    def get_dataset_id(self, dataset_name: str) -> str:
        self.client.check_token_expiration()
        self.get_datasets()
        dataset_missing = True

        for item in self.datasets:
            if item['name'] == dataset_name:
                logging.info(f"Found dataset with name {dataset_name} and dataset id {item['id']} in My Workspace.")
                self.dataset = {dataset_name: item['id']}
                dataset_missing = False
                return self.dataset
        if dataset_missing:
            logging.warning(f"Unable to find dataset with name: {dataset_name} in My Workspace'")

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset-in-group
    def get_dataset_in_workspace_id(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_datasets_in_workspace(workspace_name)
        dataset_missing = True

        for item in self.datasets:
            if item['name'] == dataset_name:
                logging.info(f"Found dataset with name {dataset_name} and dataset id {item['id']} in workspace '{workspace_name}'.")
                self.dataset = {dataset_name: item['id']}
                dataset_missing = False
                return self.dataset
        if dataset_missing:
            logging.warning(f"Unable to find dataset with name: {dataset_name} in workspace {workspace_name}.")

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
            logging.info(f"Successfully retrieved parameters from dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_parameters = response.content
            return self.dataset_parameters
        else:
            logging.error(f"Failed to retrieve parameters from dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasources-in-group
    def get_datasources(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/datasources"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved datasources from dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_datasources = response.json()["value"]
            return self.dataset_datasources
        else:
            logging.error(f"Failed to retrieve datasources from dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/take-over-in-group
    def take_dataset_owner(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/Default.TakeOver"
        
        response = requests.post(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully took over dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_json = json.dumps(response.json(), indent=10)
            return self.dataset_json
        else:
            logging.error(f"Failed to take over dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/refresh-dataset-in-group
    def refresh_dataset(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/refreshes"
        
        response = requests.post(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_accepted_code:
            logging.info(f"Successfully start refreshing dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_json = json.dumps(response.json(), indent=10)
            return self.dataset_json
        else:
            logging.error(f"Failed to start refreshing dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history-in-group
    def get_dataset_refresh_history(self, dataset_name: str, workspace_name: str, topN: int = None) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/refreshes"
        if topN: url = url + f'?$top={topN}'
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved refresh history from dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_refreshes = response.json()["value"]
            return self.dataset_refreshes
        else:
            logging.error(f"Failed to retrieve refresh history from dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    def get_refresh_history_in_dataset_id(self, dataset_name: str, workspace_name: str, refresh_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_refresh_history(dataset_name, workspace_name)
        refresh_missing = True

        for item in self.dataset_refreshes:
            if item['name'] == refresh_name:
                logging.info(f"Found refresh {refresh_name} for dataset {dataset_name} in workspace {workspace_name}.")
                self.dataset_refresh = {refresh_name: item['requestId']}
                refresh_missing = False
                return self.dataset_refresh
        if refresh_missing:
            logging.warning(f"Unable to find refresh {refresh_name} for dataset with name {dataset_name} in workspace {workspace_name}.")
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history-in-group
    def get_dataset_refresh_details(self, dataset_name: str, workspace_name: str, refresh_name: str) -> str:
        self.client.check_token_expiration()
        self.get_refresh_history_in_dataset_id(dataset_name, workspace_name, refresh_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/refreshes/" + self.dataset_refresh[refresh_name]

        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code or response.status_code == self.client.http_accepted_code:
            logging.info(f"Successfully retrieved details for refresh {refresh_name} from dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_refresh_details = response.json()
            return self.dataset_refresh_details
        else:
            logging.error(f"Failed to retrieve details for refresh {refresh_name} from dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-schedule-in-group
    def get_dataset_refresh_schedule(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/refreshSchedule"

        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved refresh schedule from dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_refresh_schedule = response.json()
            return self.dataset_refresh_schedule
        else:
            logging.error(f"Failed to retrieve refresh schedule from dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)