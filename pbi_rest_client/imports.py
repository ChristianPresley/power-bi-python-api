#!/usr/bin/env python

import logging
import datetime
import requests
import os
import json

from typing import List
import binascii
from urllib import parse

from .rest_client import RestClient
from .workspaces import Workspaces

class Imports:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self.workspaces = Workspaces(authz_header, token, token_expiration)

    def import_file_into_workspace(self, workspace_name: str, skip_report: bool, file_path: str, display_name: str) -> None:
        self.workspaces.get_workspace_id(workspace_name)

        if not os.path.isfile(file_path):
            raise FileNotFoundError(2, f"No such file or directory: '{file_path}'. Please check the file exists and try again.")
        
        url = self.client.base_url + f"groups/{self.workspaces._workspace[workspace_name]}/imports?datasetDisplayName=model.json&nameConflict=Abort&skipReport=True"
        
        files = {
            'value': ("Content-Disposition: form-data name=model.json; filename=model.json Content-Type: application/json", open(file_path, 'rb'))
        }

        response = requests.post(url, headers = self.client.multipart_headers, files = files)

        print (response.content)

        if response.status_code == 202:
            logging.info(response.json())
            import_id = response.json()["id"]
            logging.info(f"Uploading file uploading with id: {import_id}")
        else:
            self.client.force_raise_http_error(response)

        get_import_url = self.client.base_url + f"groups/{self.workspaces._workspace[workspace_name]}/imports/{import_id}"
        
        while True:
            response = requests.get(url = get_import_url, headers = self.client.multipart_headers)

            if response.status_code != 200:
                logging.error("Failed to upload file to workspace.")
                self.force_raise_http_error(response)
            if response.json()["importState"] == "Succeeded":
                logging.info(f"Successfully imported file to workspace {workspace_name}.")
                return
            else:
                logging.info("Import is currently in progress. . . Please wait.")