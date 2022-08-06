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
        self.dataset_refresh_cancelled = False
        self.dataset_deleted = False
        self.dataset_gateways = None
        self.dataset_permission_updated = False
        self.dataset_users = False
        self.user = {}

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset
    # Get specific dataset from My Workspace
    def get_dataset(self, dataset_id: str) -> str:
        self.client.check_token_expiration()

        url = self.client.base_url + "datasets/" + dataset_id
        
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

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/bind-to-gateway-in-group
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
    # Get all Datasets from My Workspace
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
    def refresh_dataset(self, dataset_name: str, workspace_name: str, refresh_type: str = None) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/refreshes"
        
        # enable Enhanced refresh (Premium/PPU or Embedded) which can be cancelled
        # https://docs.microsoft.com/en-us/power-bi/connect-data/asynchronous-refresh
        if refresh_type in ['Automatic', 'Calculate', 'ClearValues', 'DataOnly', 'Defragment', 'Full']:
            payload = {
                "type": refresh_type
            }
            response = requests.post(url, json = payload, headers = self.client.json_headers)
        else :
            response = requests.post(url, headers = self.client.json_headers)


        if response.status_code == self.client.http_accepted_code:
            logging.info(f"Successfully start refreshing dataset {dataset_name} in workspace {workspace_name}.")
            # self.dataset_json = json.dumps(response.json(), indent=10)
            self.dataset_refreshing = True
            return self.dataset_refreshing
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
            if item['requestId'] == refresh_name:
                logging.info(f"Found refresh {refresh_name} for dataset {dataset_name} in workspace {workspace_name}.")
                self.dataset_refresh = {refresh_name: item['requestId']}
                refresh_missing = False
                return self.dataset_refresh
        if refresh_missing:
            logging.warning(f"Unable to find refresh {refresh_name} for dataset with name {dataset_name} in workspace {workspace_name}.")
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-execution-details-in-group
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

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/cancel-refresh-in-group
    def cancel_dataset_refresh(self, dataset_name: str, workspace_name: str) -> bool:
        self.client.check_token_expiration()
        self.get_dataset_refresh_history(dataset_name, workspace_name)

        refresh_missing =True
        self.dataset_refresh_cancelled = False

        for refresh in self.dataset_refreshes:
            if refresh['status'] == 'Unknown' and refresh['refreshType'] == 'ViaEnhancedApi':
                refresh_name = refresh['requestId']
                refresh_missing = False
                break
        if refresh_missing:
            logging.warning(f"Unable to find active refresh for dataset with name {dataset_name} in workspace {workspace_name}.")
            return self.dataset_refresh_cancelled
        
        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/refreshes/" + refresh_name
        
        response = requests.delete(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully cancelled refresh for dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_refresh_cancelled = True
            return self.dataset_refresh_cancelled
        else:
            logging.error(f"Failed to cancel refresh for dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/delete-dataset-in-group
    def delete_dataset(self, dataset_name: str, workspace_name: str) -> bool:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        self.dataset_deleted = False

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name]

        response = requests.delete(url, headers = self.client.json_headers)
        
        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully deleted dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_deleted = True
            return self.dataset_deleted
        else:
            logging.error(f"Failed to delete dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/discover-gateways-in-group
    def get_dataset_gateways(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/Default.DiscoverGateways"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved list of gateways for dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_gateways = response.json()["value"]
            return self.dataset_gateways
        else:
            logging.error(f"Failed to retrieve gateway for dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset-users-in-group
    def get_dataset_users(self, dataset_name: str, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/users"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved list of users for dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_users = response.json()["value"]
            return self.dataset_users
        else:
            logging.error(f"Failed to retrieve list of users for dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset-users-in-group
    def get_user_in_dataset_id(self, dataset_name: str, workspace_name: str, user_name: str) -> str:
        self.client.check_token_expiration()
        self.get_dataset_users(dataset_name, workspace_name)
        user_missing = True
        self.user = ''

        for item in self.dataset_users:
            if item['identifier'] == user_name:
                logging.info(f"Found user {user_name} for dataset {dataset_name} in workspace '{workspace_name}'.")
                self.user = {'user' : user_name, 'User Type': item['principalType'], 'Permission': item['datasetUserAccessRight'] }
                user_missing = False
                return self.user
        if user_missing:
            logging.warning(f"Unable to find user {user_name} in access list for dataset {dataset_name} in workspace {workspace_name}.")
    
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/post-dataset-user-in-group
    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/put-dataset-user-in-group
    def update_dataset_user_permission(self, dataset_name: str, workspace_name: str, user_name: str, access_type: str, principal_type: str) -> bool:
        self.client.check_token_expiration()
        self.get_dataset_in_workspace_id(dataset_name, workspace_name)
        self.get_user_in_dataset_id(dataset_name, workspace_name, user_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/datasets/" + self.dataset[dataset_name] + "/users"
        
        self.dataset_permission_updated = False
        error_parameter = ''
        
        if principal_type not in ['App', 'Group', 'None', 'User']:
            error_parameter = 'principal type'
        elif access_type not in ['Read', 'ReadExplore', 'ReadReshare', 'ReadReshareExplore']:
            error_parameter = 'access type'
        if error_parameter != '':
            logging.error(f'Issue with updating permission to {user_name} due to incorrect {error_parameter} for dataset {dataset_name} in workspace {workspace_name}.')
            return None
        
        payload = {
                "identifier": user_name, 
                "principalType": principal_type,
                "datasetUserAccessRight": access_type
            }

        if self.user['user'] != user_name:
            response = requests.post(url, json = payload, headers = self.client.json_headers)
        else:
            response = requests.put(url, json = payload, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully updating permission to {user_name} with access {access_type} as {principal_type} for dataset {dataset_name} in workspace {workspace_name}.")
            self.dataset_permission_updated = True
            return self.dataset_permission_updated
        else:
            logging.error(f"Failed to update permission to {user_name} for dataset {dataset_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    