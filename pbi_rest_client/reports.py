#!/usr/bin/env python

import os
import logging
import requests

from azure.storage.blob import BlobClient
from typing import List

from .rest_client import RestClient
from .workspaces import Workspaces

class Reports:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self.workspaces = Workspaces(authz_header, token, token_expiration)
        self._reports = None
        self._report = {}
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/get-reports-in-group
    def get_reports(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/reports"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved reports in workspace: " + workspace_name)
            self._reports = response.json()["value"]
            return self._reports
        else:
            logging.error("Failed to retrieve reports in workspace: " + workspace_name)
            self.client.force_raise_http_error(response)
    
    def get_report(self, workspace_name: str, report_name: str) -> List:
        self.client.check_token_expiration()
        self.get_reports(workspace_name)
        report_found = False

        for item in self._reports:
            if item['name'] == report_name:
                logging.info("Found report with name: " + report_name + " in workspace with name: " + workspace_name)
                report_found = True
                self._report = item
                return self._report
        
        if report_found == False:
            logging.warn("Unable to find report with name: " + report_name + " in workspace with name: " + workspace_name)
            return None

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/export-report-in-group
    def export_report(self, workspace_name: str, report_name: str, container_name: str, chunk_size = 128) -> None:
        self.client.check_token_expiration()
        self.get_report(workspace_name, report_name)
        out_file = report_name + ".pbix"

        blob = BlobClient.from_connection_string(conn_str=os.getenv('AZURE_STORAGE'), container_name=f"{container_name}", blob_name=f"{report_name}.pbix")
        url = self.client.base_url + "groups/" + self.workspaces._workspace[workspace_name] + "/reports/" + self._report['id'] + "/Export"
        
        response = requests.get(url, headers = self.client.json_headers, stream = True)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully exported report: " + report_name + " in workspace: " + workspace_name)
            with open(out_file, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    fd.write(chunk)
            with open(out_file, "rb") as fd:
                blob.upload_blob(fd, overwrite = True)
            return logging.info("Exported PBIX file to: " + out_file)
        else:
            logging.error("Failed to export report: " + report_name + " in workspace: " + workspace_name)
            self.client.force_raise_http_error(response)