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
from .dataflows import Dataflows
from .reports import Reports

class Imports:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self.workspaces = Workspaces(authz_header, token, token_expiration)
        self.dataflows = Dataflows(authz_header, token, token_expiration)
        self.reports = Reports(authz_header, token, token_expiration)
        self._dataflow_name = None

    # https://docs.microsoft.com/en-us/rest/api/power-bi/imports/post-import
    def import_file_into_workspace(self, workspace_name: str, display_name: str, file_name: str, **kwargs) -> None:
        restore_from_blob = kwargs.get('restore_from_blob', False)
        blob_container_name = kwargs.get('blob_container_name', None)
        dataflow = kwargs.get('dataflow', False)
        skip_report = kwargs.get('skip_report', False)
        ''' Imports files into Power BI
        Args:
            workspace_name (string): The name of the workspace in Power BI. Service Account must have permissions to write to the workspace.
            display_name (string): The display name that will be assigned to the objects imported into the Power BI workspace.
        Returns:
            string: Requests HTTP Response
        '''

        self.workspaces.get_workspace_id(workspace_name)

        if restore_from_blob:
            blob = BlobClient.from_connection_string(conn_str=os.getenv('AZURE_STORAGE'), container_name=blob_container_name, blob_name=file_name)
            with open(file_name, 'wb') as file:
                data = blob.download_blob()
                file.write(data.readall())

        if not os.path.isfile(file_name):
            raise FileNotFoundError(2, f"No such file or directory: '{file_name}'. Please check the file exists and try again.")
        
        if dataflow:
            display_name = 'model.json'
            with open(file_name, 'r') as f:
                json_data = json.load(f)
                self._dataflow_name = json_data['name']
                self.dataflows.get_dataflow(workspace_name, self._dataflow_name)

        url = (
            f"{self.client.base_url}"
            + "groups/"
            + f"{self.workspaces._workspace[workspace_name]}"
            + "/imports?"
            + f"datasetDisplayName={display_name}"
            + ("&nameConflict=Abort" if dataflow else "&nameConflict=CreateOrOverwrite")
            + ("&skipReport=true" if skip_report else "")
        )

        if dataflow:
            if self.dataflows._dataflow != None:
                self.dataflows.delete_dataflow(workspace_name, self._dataflow_name)
            files = {
                'value': ("Content-Disposition: form-data name=model.json; filename=model.json Content-Type: application/json", open(file_name, 'rb'))
            }
        else:
            files = {
                'filename': open(file_name, 'rb')
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
