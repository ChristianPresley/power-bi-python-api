#!/usr/bin/env python

import logging
import datetime
import requests
import os
import json

from azure.storage.blob import BlobClient
from typing import List
from urllib import parse

from .rest_client import RestClient
from .workspaces import Workspaces

class Imports:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self.workspaces = Workspaces(authz_header, token, token_expiration)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/imports/post-import
    def import_file_into_workspace(self, workspace_name: str, display_name: str, file_path: str, file_name: str, dataflow: bool, skip_report: bool) -> None:
        self.workspaces.get_workspace_id(workspace_name)
        full_path = file_path + file_name

        if not os.path.isfile(full_path):
            raise FileNotFoundError(2, f"No such file or directory: '{full_path}'. Please check the file exists and try again.")
        
        url = (
            f"{self.client.base_url}"
            + "groups/"
            + f"{self.workspaces._workspace[workspace_name]}"
            + "/imports?"
            + f"datasetDisplayName={display_name}"
            + "&nameConflict=CreateOrOverwrite"
            + ("&skipReport=true" if skip_report else "")
        )

        if dataflow:
            files = {
                'value': ("Content-Disposition: form-data name=model.json; filename=model.json Content-Type: application/json", open(full_path, 'rb'))
            }
        else:
            files = {
                'filename': open(full_path, 'rb')
            }

        response = requests.post(url, headers = self.client.multipart_headers, files = files)

        if response.status_code == self.client.http_accepted_code:
            logging.info(response.json())
            import_id = response.json()["id"]
            logging.info(f"Uploading file uploading with id: {import_id}")
        else:
            self.client.force_raise_http_error(response)

        get_import_url = self.client.base_url + f"groups/{self.workspaces._workspace[workspace_name]}/imports/{import_id}"
        
        while True:
            response = requests.get(url = get_import_url, headers = self.client.multipart_headers)

            if response.status_code != self.client.http_ok_code:
                logging.error("Failed to upload file to workspace.")
                self.client.force_raise_http_error(response)
            if response.json()["importState"] == "Succeeded":
                logging.info(f"Successfully imported file to workspace {workspace_name}.")
                return
            else:
                logging.info("Import is currently in progress. . . Please wait.")
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/imports/post-import
    def import_file_from_blob_into_workspace(self, workspace_name: str, display_name: str, blob_container: str, blob_name: str, dataflow: bool, skip_report: bool) -> None:
        self.workspaces.get_workspace_id(workspace_name)

        blob = BlobClient.from_connection_string(conn_str=os.getenv('AZURE_STORAGE'), container_name=blob_container, blob_name=blob_name)
        with open(blob_name, 'wb') as file:
            data = blob.download_blob()
            file.write(data.readall())

        if not os.path.isfile(blob_name):
            raise FileNotFoundError(2, f"No such file or directory: '{blob_name}'. Please check the file exists and try again.")
        
        url = (
            f"{self.client.base_url}"
            + "groups/"
            + f"{self.workspaces._workspace[workspace_name]}"
            + "/imports?"
            + f"datasetDisplayName={display_name}"
            + "&nameConflict=CreateOrOverwrite"
            + ("&skipReport=true" if skip_report else "")
        )

        if dataflow:
            files = {
                'value': ("Content-Disposition: form-data name=model.json; filename=model.json Content-Type: application/json", open(blob_name, 'rb'))
            }
        else:
            files = {
                'filename': open(blob_name, 'rb')
            }

        response = requests.post(url, headers = self.client.multipart_headers, files = files)

        if response.status_code == self.client.http_accepted_code:
            logging.info(response.json())
            import_id = response.json()["id"]
            logging.info(f"Uploading file uploading with id: {import_id}")
        else:
            self.client.force_raise_http_error(response)

        get_import_url = self.client.base_url + f"groups/{self.workspaces._workspace[workspace_name]}/imports/{import_id}"
        
        while True:
            response = requests.get(url = get_import_url, headers = self.client.multipart_headers)

            if response.status_code != self.client.http_ok_code:
                logging.error("Failed to upload file to workspace.")
                self.client.force_raise_http_error(response)
            if response.json()["importState"] == "Succeeded":
                logging.info(f"Successfully imported file to workspace {workspace_name}.")
                return
            else:
                logging.info("Import is currently in progress. . . Please wait.")
    