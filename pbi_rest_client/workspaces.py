#!/usr/bin/env python

import logging
import requests

from typing import List

class Workspaces:
    def __init__(self, client):
        self.client = client
        self.workspaces = None
        self.workspace = {}
        self.workspace_users = None
        self.user = {}
        self.user_missing = False
    
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
            self.workspaces = response.json()["value"]
            return self.workspaces
        else:
            logging.error("Failed to retrieve workspaces.")
            self.client.force_raise_http_error(response)

    def get_workspace_id(self, workspace_name: str) -> str:
        self.client.check_token_expiration()
        self.get_workspaces()
        workspace_missing = True

        for item in self.workspaces:
            if item['name'] == workspace_name:
                logging.info(f"Found workspace with name {workspace_name} and workspace id {item['id']}.")
                self.workspace = {workspace_name: item['id']}
                workspace_missing = False
                return self.workspace
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

    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/get-group-users
    def get_workspace_users(self, workspace_name) -> List:
        self.client.check_token_expiration()
        self.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspace[workspace_name] + "/users"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspace users.")
            self.workspace_users = response.json()["value"]
            return self.workspace_users
        else:
            logging.error("Failed to retrieve workspace users.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/add-group-user
    def add_user_to_workspace(self, workspace_name: str, principal_id: str, access_right: str, service_principal: bool, group: bool, user_account: bool) -> bool:
        self.client.check_token_expiration()
        self.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspace[workspace_name] + "/users"

        if service_principal and not group and not user_account:
            principal_type = "App"
        elif group and not service_principal and not user_account:
            principal_type = "User"
        elif user_account and not service_principal and not group:
            principal_type = "Group"
        else:
            logging.error("Only one principal type can be specified.")
            return False
        
        request_payload = {
            "identifier": principal_id,
            "groupUserAccessRight": access_right,
            "principalType": principal_type
        }

        response = requests.post(url, json = request_payload, headers = self.client.json_headers)
                   
        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully assigned user to workspace: {workspace_name}.")
            return True
        else:
            logging.error(f"Failed to assign user to workspace: {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/get-groups
    def get_workspaces_as_admin(self, topN = 100) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "admin/groups" + f'?$top={topN}'
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved workspaces.")
            self.workspaces = response.json()["value"]
            return self.workspaces
        else:
            logging.error("Failed to retrieve workspaces.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/delete-group
    def delete_workspace(self, workspace_name: str) -> bool:
        self.client.check_token_expiration()
        self.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspace[workspace_name]

        response = requests.delete(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully deleted workspaces {workspace_name}.")
            return True
        else:
            logging.error(f"Failed to delete workspaces {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset-users-in-group
    def get_user_in_workspace_id(self, workspace_name: str, user_name: str) -> str:
        self.client.check_token_expiration()
        self.get_workspace_users(workspace_name)
        self.user_missing = True
        self.user = {}

        for item in self.workspace_users:
            if item['identifier'] == user_name:
                logging.info(f"Found user {user_name} in workspace '{workspace_name}'.")
                self.user = {'Display Name': item['displayName'], 'user' : item['identifier'], 'User Type': item['principalType'], 'Permission': item['groupUserAccessRight'] }
                self.user_missing = False
                return self.user
        if self.user_missing:
            logging.warning(f"Unable to find user {user_name} in workspace {workspace_name}.")

    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/delete-user-in-group
    def delete_user_from_workspace(self, workspace_name: str, user_name: str) -> bool:
        self.client.check_token_expiration()
        self.get_workspace_id(workspace_name)
        self.get_user_in_workspace_id(workspace_name, user_name)

        if self.user_missing:
            logging.info(f"Unable to delete user {user_name} from workspace {workspace_name} as not present in user list.")
            return False
        
        url = self.client.base_url + "groups/" + self.workspace[workspace_name] + "/users/" + self.user['user']

        response = requests.delete(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully deleted user {user_name} from workspace {workspace_name}.")
            return True
        else:
            logging.error(f"Failed to delete user {user_name} from workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/add-group-user
    # https://docs.microsoft.com/en-us/rest/api/power-bi/groups/update-group-user
    def update_user_in_workspace(self, workspace_name: str, user_name: str, access_type: str, principal_type: str) -> bool:
        self.client.check_token_expiration()
        self.get_workspace_id(workspace_name)
        self.get_user_in_workspace_id(workspace_name, user_name)

        url = self.client.base_url + "groups/" + self.workspace[workspace_name] + "/users"
        
        error_parameter = ''
        
        if principal_type not in ['App', 'Group', 'None', 'User']:
            error_parameter = 'principal type'
        elif access_type not in ['Admin', 'Contributor', 'Member', 'None', 'Viewer']:
            error_parameter = 'access type'
        if error_parameter != '':
            logging.error(f'Issue with updating permission for {user_name} due to incorrect {error_parameter} for workspace {workspace_name}.')
            return False

        payload = {
            "identifier": user_name,
            "groupUserAccessRight": access_type,
            "principalType": principal_type
        }

        if self.user_missing:
            response = requests.post(url, json = payload, headers = self.client.json_headers)
        else:
            response = requests.put(url, json = payload, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully updated user acces for user {user_name} to workspace {workspace_name}.")
            return True
        else:
            logging.error(f"Failed to aupdate user acces for user {user_name} to workspace {workspace_name}.")
            self.client.force_raise_http_error(response)
    