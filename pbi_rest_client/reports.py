#!/usr/bin/env python

import os
import logging
import requests

from typing import List
import json

try:
    utils_enable = True
    from .utils.utils import Utils
except:
    utils_enable = False
from .workspaces import Workspaces
from .datasets import Datasets

if utils_enable:
    utils = Utils()

class Reports:
    def __init__(self, client):
        self.client = client
        self.workspaces = Workspaces(client)
        self.datasets = Datasets(client)
        self.reports = None
        self.report = None
        self.report_datasources = None
        self.report_pages = None
        self.transfer_ownership = False
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/get-reports-in-group
    def get_reports(self, workspace_name: str) -> List:
        self.client.check_token_expiration()
        self.workspaces.get_workspace_id(workspace_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved reports in workspace: " + workspace_name)
            self.reports = response.json()["value"]
            return self.reports
        else:
            logging.error("Failed to retrieve reports in workspace: " + workspace_name)
            self.client.force_raise_http_error(response)
    
    def get_report(self, workspace_name: str, report_name: str) -> List:
        self.client.check_token_expiration()
        self.get_reports(workspace_name)
        report_found = False

        for item in self.reports:
            if item['name'] == report_name:
                logging.info("Found report with name: " + report_name + " in workspace with name: " + workspace_name)
                report_found = True
                self.report = item
                return self.report
        
        if report_found == False:
            logging.warn("Unable to find report with name: " + report_name + " in workspace with name: " + workspace_name)
            return None

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/export-report-in-group
    def export_report(self, workspace_name: str, report_name: str, chunk_size = 128) -> None:
        if not utils_enable:
            return logging.warning(f"Failed to export report {report_name} in workspace {workspace_name} due to issue with Azure credentials.")

        self.client.check_token_expiration()
        self.get_report(workspace_name, report_name)

        out_file = report_name + ".pbix"
        blob = utils.blob_client(out_file)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports/" + self.report['id'] + "/Export"
        
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

    # https://docs.microsoft.com/en-us/rest/api/power-bi/datasets/get-dataset-in-group
    def get_report_in_workspace_id(self, workspace_name: str, report_name: str) -> str:
        self.client.check_token_expiration()
        self.get_reports(workspace_name)
        report_missing = True

        for item in self.reports:
            if item['name'] == report_name:
                logging.info(f"Found report with name {report_name} and report id {item['id']} in workspace '{workspace_name}'.")
                self.report = {report_name: item['id']}
                report_missing = False
                return self.report
        if report_missing:
            logging.warning(f"Unable to find report with name {report_name} in workspace {workspace_name}.")

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/clone-report-in-group
    def clone_report(self, workspace_name: str, report_name: str, clone_report_name: str, target_workspace_name: str = None, target_dataset_name: str = None, target_dataset_workspace_name: str = None) -> bool:
        self.client.check_token_expiration()
        self.get_report(workspace_name, report_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports/" + self.report['id'] + "/Clone"

        if not target_dataset_name:
            target_dataset_name = self.report['datasetId']
        elif target_dataset_workspace_name != None and target_dataset_name != None:
            self.datasets.get_dataset_in_workspace_id(target_dataset_name, target_dataset_workspace_name)
            target_dataset_name = self.datasets.dataset[target_dataset_name]
        elif target_dataset_name != None:
            self.datasets.get_dataset_in_workspace_id(target_dataset_name, workspace_name)
            target_dataset_name = self.datasets.dataset[target_dataset_name]
        
        if not target_workspace_name:
            target_workspace_name = self.workspaces.workspace[workspace_name]
        elif target_workspace_name.lower() == 'my workspace':
            target_workspace_name = '00000000-0000-0000-0000-000000000000'
        else:
            self.workspaces.get_workspace_id(target_workspace_name)
            target_workspace_name = self.workspaces.workspace[workspace_name]
        
        payload = {
                "name": clone_report_name,
                "targetModelId": target_dataset_name,
                "targetWorkspaceId": target_workspace_name
            }

        response = requests.post(url, json = payload, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully clone report {report_name} from workspace {workspace_name} as report {clone_report_name} in workspace {target_workspace_name} using dataset {target_dataset_name}.")
            return True
        else:
            logging.error(f"Failed to clone report {report_name} from workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/delete-report-in-group
    def delete_report(self, workspace_name: str, report_name: str) -> bool:
        self.client.check_token_expiration()
        self.get_report_in_workspace_id(workspace_name, report_name)

        self.dataset_deleted = False

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports/" + self.report[report_name]

        response = requests.delete(url, headers = self.client.json_headers)
        
        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully deleted report {report_name} in workspace {workspace_name}.")
            self.dataset_deleted = True
            return self.dataset_deleted
        else:
            logging.error(f"Failed to delete report {report_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/get-datasources-in-group
    def get_datasources_for_paginated_report(self, workspace_name: str, report_name: str) -> List:
        self.client.check_token_expiration()
        self.get_report(workspace_name, report_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports/" + self.report['id'] + "/datasources"

        if self.report['reportType'] != 'PaginatedReport':
            logging.warning(f"Failed to get datasources from report {report_name} because it not a pagniated report.")
            return None

        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved datasources from report {report_name} in workspace {workspace_name}.")
            self.report_datasources = response.json()["value"]
            return self.report_datasources
        else:
            logging.error(f"Failed to retrieve datasources from report {report_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/get-pages-in-group
    def get_report_pages(self, workspace_name: str, report_name: str) -> List:
        self.client.check_token_expiration()
        self.get_report_in_workspace_id(workspace_name, report_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports/" + self.report[report_name] + "/pages"

        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved list of pages for report {report_name} in workspace {workspace_name}.")
            self.report_pages = response.json()["value"]
            return self.report_pages
        else:
            logging.error(f"Failed to retrieve list of pages for report{report_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/rebind-report-in-group
    def rebind_report(self, workspace_name: str, report_name: str, target_dataset_name: str = None, target_dataset_workspace_name: str = None) -> bool:
        self.client.check_token_expiration()
        self.get_report(workspace_name, report_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports/" + self.report['id'] + "/Rebind"

        if not target_dataset_name:
            target_dataset_name = self.report['datasetId']
        elif target_dataset_workspace_name != None and target_dataset_name != None:
            self.datasets.get_dataset_in_workspace_id(target_dataset_name, target_dataset_workspace_name)
            target_dataset_name = self.datasets.dataset[target_dataset_name]
        elif target_dataset_name != None:
            self.datasets.get_dataset_in_workspace_id(target_dataset_name, workspace_name)
            target_dataset_name = self.datasets.dataset[target_dataset_name]

        payload = {
                "datasetId": target_dataset_name
            }

        response = requests.post(url, json = payload, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully rebind report {report_name} in workspace {workspace_name} from dataset {self.report['id']} to dataset {target_dataset_name}.")
            return True
        else:
            logging.error(f"Failed to rebind report {report_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/update-datasources-in-group
    def update_datasources_for_paginated_report(self, workspace_name: str, report_name: str, datasource_names: List, server_names: List, database_names: List) -> bool:
        self.client.check_token_expiration()
        self.get_report(workspace_name, report_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports/" + self.report['id'] + "/Default.UpdateDatasources"

        if self.report['reportType'] != 'PaginatedReport':
            logging.warning(f"Failed to get datasources from report {report_name} because it not a pagniated report.")
            return False
        if self.report['isOwnedByMe'] != True:
            self.become_owner_of_paginated_report_datasources(workspace_name, report_name)

        if not self.transfer_ownership:
            logging.warning(f"Failed to transfer report ownership for report {report_name}, datasources not updated.")
            return False
        if len(datasource_names) != len(server_names) and len(datasource_names) != len(database_names):
            logging.warning(f"Datasource_names, server_names and database_names list do not have the same number of items! {report_name} datasources' report were not updated.")
            return False

        datasource_count = len(datasource_names)
        datasource_string = ''
        for i in range(datasource_count):
            datasource_string = datasource_string + '{"datasourceName": " ' + datasource_names[i] + '", "connectionDetails": { "server": " ' + server_names[i] + '", "database":" ' + database_names[i] + '" } }'
            if i < datasource_count-1:
                datasource_string = datasource_string + ', '
        
        payload = '{ "updateDetails": [ ' + datasource_string + '] } '

        response = requests.post(url, json = json.loads(payload), headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully update datasources for report {report_name} in workspace {workspace_name}.")
            return True
        else:
            logging.error(f"Failed to update datasources for report {report_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/take-over-in-group
    def become_owner_of_paginated_report_datasources(self, workspace_name: str, report_name: str) -> bool:
        self.client.check_token_expiration()
        self.get_report(workspace_name, report_name)
        self.transfer_ownership = False
        
        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports/" + self.report['id'] + "/Default.TakeOver"

        if self.report['reportType'] != 'PaginatedReport':
            logging.warning(f"Failed to get datasources from report {report_name} because it not a pagniated report.")
            return None

        response = requests.post(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully transfered ownership of datasources for paginated report {report_name} in workspace {workspace_name}.")
            self.transfer_ownership = True
            return self.transfer_ownership
        else:
            logging.error(f"Failed to transfer ownership of datasources for paginated report {report_name} in workspace {workspace_name}.")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/reports/update-report-content-in-group#sourcetype
    def update_report_content(self, workspace_name: str, report_name: str, source_workspace_name: str, source_report_name: str) -> bool:
        self.client.check_token_expiration()
        
        self.get_report_in_workspace_id(source_workspace_name, source_report_name)
        source_workspace_name_id = self.workspaces.workspace[workspace_name]
        source_report_name_id = self.report[source_report_name]
        
        self.get_report_in_workspace_id(workspace_name, report_name)

        url = self.client.base_url + "groups/" + self.workspaces.workspace[workspace_name] + "/reports/" + self.report[report_name] + "/UpdateReportContent"

        payload = {
                    "sourceReport": {
                        "sourceReportId": source_report_name_id,
                        "sourceWorkspaceId": source_workspace_name_id
                    },
                    "sourceType": "ExistingReport"
            }

        response = requests.post(url, json = payload, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully update report content for {report_name} in workspace {workspace_name} from report {source_workspace_name} in workspace {source_report_name}.")
            return True
        else:
            logging.error(f"Failed to update report content for {report_name} in workspace {workspace_name} from report {source_workspace_name} in workspace {source_report_name}.")
            self.client.force_raise_http_error(response)