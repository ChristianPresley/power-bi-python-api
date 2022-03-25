import requests
import datetime
import logging
import os

from typing import Callable, Dict, List, NoReturn, Union
from urllib import parse
from power_bi_api_client.utils import partition

HTTP_OK_CODE = 200
HTTP_CREATED_CODE = 201
HTTP_ACCEPTED_CODE = 202

def check_bearer_token(fn: Callable) -> Callable:
    def wrapper(pbi_client, *args, **kwargs):
        if pbi_client.token is None:
            logging.info(f"Access token does not exist. Attempting to generate access token.")
            pbi_client.update_bearer_token()
        elif pbi_client.token_expiration < datetime.datetime.utcnow():
            logging.info(f"Access token has expired. Attempting to renew access token.")
            pbi_client.update_bearer_token()
        return fn(pbi_client, *args, **kwargs)
    return wrapper

class PowerBIAPIClient:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.powerbi.com/v1.0/myorg/"
        self.url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.token = None
        self.token_expiration = None
        self._workspaces = None
        self._pipelines = None
        self.headers = None

    def get_authz_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def update_bearer_token(self) -> None:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "https://analysis.windows.net/powerbi/api/.default",
        }
        
        response = requests.post(self.url, data=payload, headers=headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully retrieved access token for client id {self.client_id}.")
            self.token = response.json()["access_token"]
            self.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            self.headers = {**headers, **self.get_authz_header()}
        else:
            logging.error(f"Failed to retrieve access token for client id {self.client_id}.")
            self.force_raise_http_error(response)

    @property
    def workspaces(self) -> List:
        return self._workspaces or self.get_workspaces()

    @check_bearer_token
    def get_workspace(self, workspace_name: str) -> List:
        url = self.base_url + "groups?$filter=" + parse.quote(f"name eq '{workspace_name}'")
        
        response = requests.get(url, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info("Successfully retrieved workspace.")
            return response.json()["value"]
        else:
            logging.error("Failed to retrieve workspace.")
            self.force_raise_http_error(response)
    
    @check_bearer_token
    def get_workspaces(self) -> List:
        url = self.base_url + "groups"
        
        response = requests.get(url, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info("Successfully retrieved workspaces.")
            return response.json()["value"]
        else:
            logging.error("Failed to retrieve workspaces.")
            self.force_raise_http_error(response)
            
    @property
    def pipelines(self) -> List:
        return self._pipelines or self.get_pipelines()
    
    @check_bearer_token
    def get_pipelines(self) -> List:
        url = self.base_url + "pipelines"
        
        response = requests.get(url, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info("Successfully retrieved pipelines.")
            return response.json()["value"]
        else:
            logging.error("Failed to retrieve pipelines.")
            self.force_raise_http_error(response)

    @staticmethod
    def find_entity_id_by_name(entity_list: List, name: str, entity_type: str, raise_if_missing: bool = False) -> str:
        for item in entity_list:
            if entity_type == "workspace" or entity_type == "report" or entity_type == "dataset":
                if item["name"] == name:
                    return item["id"]
            if entity_type == "pipeline":
                if item["displayName"] == name:
                    return item["id"]
        if raise_if_missing:
            raise RuntimeError(f"Unable to find {entity_type} with name: '{name}'")

    @check_bearer_token
    def create_workspace(self, workspace_name: str) -> None:
        url = self.base_url + "groups?$filter=" + parse.quote(f"name eq '{workspace_name}'")
        
        response = requests.get(url, headers=self.headers)

        if response.status_code != HTTP_OK_CODE:
            logging.error(f"Failed to get workspaces.")
            self.force_raise_http_error(response)

        if response.json()["@odata.count"] > 0:
            logging.info(f"The workspace {workspace_name} already exists, no changes made.")
            return response.json()

        logging.info(f"Trying to create workspace with name: {workspace_name}...")
        url = self.base_url + "groups?workspaceV2=True"
        
        response = requests.post(url, data={"name": workspace_name}, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully created workspace {workspace_name}.")
            self.get_workspaces()
            return response.json()
        else:
            logging.error(f"Failed to create workspace {workspace_name}.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def set_workspace_capacity(self, workspace_name: str, capacity: Dict) -> None:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/AssignToCapacity"
        
        response = requests.post(url, data=capacity, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully changed capacity of workspace {workspace_name} to {capacity}.")
            return response
        else:
            logging.error(f"Failed to change capacity of workspace {workspace_name} to {capacity}.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def create_pipeline(self, workspace_name: str) -> None:
        url = self.base_url + "pipelines"
        self.pipeline_exists = False
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == HTTP_OK_CODE:
            logging.info("Successfully retrieved pipelines.")
            self._pipelines = response.json()["value"]
        else:
            logging.error(f"Failed to retrieve pipelines.")
            self.force_raise_http_error(response)
        
        for object in self._pipelines:
            if object['displayName'] == f'{workspace_name}':
                logging.info(f"Successfully retrieved pipeline with name {workspace_name}.")
                self.pipeline_exists = True
                break

        if self.pipeline_exists:
            logging.warning(f"Pipeline {workspace_name} already exists, no changes made.")
            return

        logging.info(f"Attempting to create pipeline with name: {workspace_name}...")
        url = self.base_url + "pipelines"
        
        response = requests.post(url, payload={"displayName": workspace_name}, headers=self.headers)

        if response.status_code == HTTP_CREATED_CODE:
            logging.info(f"Successfully created pipeline {workspace_name}.")
            self.get_pipelines()
            return response.json()
        else:
            logging.error(f"Failed to create the new pipeline: '{workspace_name}':")
            self.force_raise_http_error(response)
    
    @check_bearer_token
    def assign_pipeline_workspace(self, pipeline_name: str, workspace_name: str, stage_order: int) -> None:
        pipeline_id = self.find_entity_id_by_name(self.pipelines, pipeline_name, "pipeline", raise_if_missing=True)
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"pipelines/{pipeline_id}/stages/{stage_order}/assignWorkspace"
        body = {
            "workspaceId": {workspace_id}
        }
                
        response = requests.post(url, data=body, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully assigned workspace with ID {workspace_id} to pipeline {pipeline_name}.")
            return response
        else:
            logging.error(f"Failed to assign workspace with ID {workspace_id} to pipeline {pipeline_name}.")
            self.force_raise_http_error(response)
    
    @check_bearer_token
    def deploy_all_pipeline_stage(self, pipeline_name: str, workspace_name: str, capacity_id: str, source_stage: str) -> None:
        source_stage_lower = source_stage.lower()
        if source_stage_lower == 'dev': stage_order = 0
        elif source_stage_lower == 'test': stage_order = 1
        
        pipeline_id = self.find_entity_id_by_name(self.pipelines, pipeline_name, "pipeline", raise_if_missing=True)
        url = self.base_url + f"pipelines/{pipeline_id}/deployAll"
        
        body = {
            "sourceStageOrder": {stage_order},
            "options": {
                "allowCreateArtifact": True,
                "allowOverwriteArtifact": True,
                "allowOverwriteTargetArtifactLabel": True,
                "allowPurgeData": True,
                "allowSkipTilesWithMissingPrerequisites": True,
                "allowTakeOver": True
            }
        }
        
        response = requests.post(url, data=body, headers=self.headers)
        
        if stage_order == 0: target_stage = 'Test'
        elif stage_order == 1: target_stage = 'Prod'

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully promoted stage {source_stage} in pipeline {pipeline_name} to {target_stage}.")
            return response
        else:
            logging.error(f"Failed to promote stage {source_stage} in pipeline {pipeline_name} to {target_stage}.")
            self.force_raise_http_error(response)
    
    @check_bearer_token
    def add_user_to_workspace(self, workspace_name: str, user: Dict) -> None:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/users"
        
        response = requests.post(url, data=user, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully added user {user} to workspace {workspace_name}.")
            return response
        else:
            logging.error(f"Failed to add user {user} to workspace {workspace_name}.")
            self.force_raise_http_error(response)
    
    @check_bearer_token
    def add_user_to_pipeline(self, pipeline_name: str, user: Dict) -> None:
        pipeline_id = self.find_entity_id_by_name(self.pipelines, pipeline_name, "pipeline", raise_if_missing=True)
        url = self.base_url + f"pipelines/{pipeline_id}/users"
        
        response = requests.post(url, data=user, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully added user {user} to pipeline {pipeline_name}.")
            return response
        else:
            logging.error(f"Failed to add user {user} to pipeline {pipeline_name}.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def get_users_from_workspace(self, workspace_name: str) -> List:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/users"

        response = requests.get(url, headers=self.headers)
        
        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully retrieved users from workspace {workspace_name}")
            return response.json()["value"]
        else:
            logging.error(f"Failed to retrieve users from workspace {workspace_name}.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def delete_workspace(self, workspace_name: str) -> None:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace")

        if workspace_id is None:
            logging.warning(f"The workspace {workspace_name} was either already deleted, does not exist, or the user does not have access.")
            return

        url = self.base_url + f"groups/{workspace_id}"
        
        response = requests.delete(url, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully deleted workspace {workspace_name}.")
            return response.json()
        else:
            logging.error(f"Failed to delete workspace {workspace_name}")
            self.force_raise_http_error(response, expected_codes = HTTP_OK_CODE)

    @check_bearer_token
    def get_datasets_in_workspace(self, workspace_name: str) -> List:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        datasets_url = self.base_url + f"groups/{workspace_id}/datasets"
        
        response = requests.get(datasets_url, headers=self.headers)
        
        response.raise_for_status()
        
        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully retrieved datasets in workspace {workspace_name}")
            return response.json()["value"]
        else:
            logging.error(f"Failed to retrieve datasets in workspace {workspace_name}.")
            self.force_raise_http_error(response, expected_codes = HTTP_OK_CODE)

    @check_bearer_token
    def refresh_dataset_by_id(self, workspace_name: str, dataset_id: str) -> None:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        response = requests.post(url, data="notifyOption=NoNotification", headers=self.headers)

        if response.status_code == HTTP_ACCEPTED_CODE:
            logging.info(f"Successfully refreshed dataset {dataset_id} in the workspace {workspace_name}).")
            return response.json()
        else:
            logging.error(f"Failed to refresh dataset {dataset_id} in the workspace {workspace_name}.")
            self.force_raise_http_error(response, expected_codes = HTTP_ACCEPTED_CODE)

    @check_bearer_token
    def refresh_dataset_by_name(self, workspace_name: str, dataset_name: str) -> None:
        datasets = self.get_datasets_in_workspace(workspace_name)
        dataset_id = self.find_entity_id_by_name(datasets, dataset_name, "dataset", True)
        self.refresh_dataset_by_id(workspace_name, dataset_id)

    @check_bearer_token
    def create_push_dataset(self, workspace_name: str, retention_policy: str) -> None:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/datasets?defaultRetentionPolicy={retention_policy}"
        
        response = requests.post(url, data="notifyOption=NoNotification", headers=self.headers)

        if response.status_code in [HTTP_CREATED_CODE, HTTP_ACCEPTED_CODE]:
            logging.info(
                f"Successfully created dataset in workspace {workspace_name} and"
                f" retention_policy: {retention_policy}"
            )
            return response.json()
        else:
            logging.error(f"Failed to create dataset in {workspace_name}.")
            self.force_raise_http_error(response, expected_codes = [HTTP_CREATED_CODE, HTTP_ACCEPTED_CODE])

    @check_bearer_token
    def create_dataset(self, workspace_name: str, schema: Dict, retention_policy: str) -> None:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/datasets?defaultRetentionPolicy={retention_policy}"
        
        response = requests.post(url, json=schema, headers=self.get_authz_header())

        if response.status_code in [HTTP_CREATED_CODE, HTTP_ACCEPTED_CODE]:
            logging.info(
                f"Successfully created dataset in workspace {workspace_name} with schema {schema}"
                f" and retention policy: {retention_policy}"
            )
            return response.json()
        else:
            logging.error(f"Failed to create dataset in workspace {workspace_name}.")
            self.force_raise_http_error(response, expected_codes = [HTTP_CREATED_CODE, HTTP_ACCEPTED_CODE])

    @check_bearer_token
    def delete_dataset(self, workspace_name: str, dataset_name: str) -> None:
        workspace_id, dataset_id = self.get_workspace_and_dataset_id(workspace_name, dataset_name)
        url = self.base_url + f"groups/{workspace_id}/datasets/{dataset_id}"
        
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully deleted dataset {dataset_id} in workspace {workspace_name}.")
            return response.json()
        else:
            logging.error(f"Failed to delete {dataset_id} in workspace {workspace_name}.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def get_tables(self, workspace_name: str, dataset_id: str) -> List:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/datasets/{dataset_id}/tables"
        
        response = requests.get(url, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully retrieved tables in dataset {dataset_id} in the workspace {workspace_name}.")
            return response.json()
        else:
            logging.error(f"Failed to retrieve tables in dataset {dataset_id} in the workspace {workspace_name}.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def delete_all_rows_in_table(self, workspace_name: str, dataset_id: str, table_name: str) -> None:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/datasets/{dataset_id}/tables/{table_name}/rows"
        
        response = requests.delete(url, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully deleted all rows in table {table_name}.")
        else:
            logging.error(f"Failed to delete rows in table {table_name}")
            self.force_raise_http_error(response)

    @check_bearer_token
    def get_reports_in_workspace(self, workspace_name: str) -> List:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/reports"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully retrieved all reports in {workspace_name}")
            return response.json()["value"]

    @check_bearer_token
    def rebind_report_in_workspace(self, workspace_name: str, dataset_name: str, report_name: str) -> None:
        workspace_id, dataset_id = self.get_workspace_and_dataset_id(workspace_name, dataset_name)
        reports = self.get_reports_in_workspace(workspace_name)
        report_id = self.find_entity_id_by_name(reports, report_name, "report", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/reports/{report_id}/Rebind"
        headers = {"Content-Type": "application/json", **self.get_authz_header()}
        payload = {"datasetId": dataset_id}

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully moved report '{report_name}' to dataset with name '{dataset_name}'.")
        else:
            logging.error(f"Failed to move report '{report_name}' to dataset with name '{dataset_name}'")
            self.force_raise_http_error(response)

    @check_bearer_token
    def delete_report(self, workspace_name: str, report_name: str) -> None:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        reports = self.get_reports_in_workspace(workspace_name)
        report_id = self.find_entity_id_by_name(reports, report_name, "report", raise_if_missing=True)
        url = self.base_url + f"groups/{workspace_id}/reports/{report_id}"
        response = requests.delete(url, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully deleted report named '{report_name}' in the workspace '{workspace_name}'.")
        else:
            logging.error(f"Failed to delete report {report_name}.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def import_file_into_workspace(
        self, workspace_name: str, skip_report: bool, file_path: str, display_name: str
    ) -> None:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)

        if not os.path.isfile(file_path):
            raise FileNotFoundError(2, f"No such file or directory: '{file_path}'. Please check the file exists and try again.")

        name_conflict = "CreateOrOverwrite"
        url = (
            self.base_url
            + f"groups/{workspace_id}/imports?datasetDisplayName={display_name}&nameConflict="
            + f"{name_conflict}"
            + ("&skipReport=True" if skip_report else "")
        )
        headers = {"Content-Type": "multipart/form-data", **self.get_authz_header()}

        with open(file_path, "rb") as f:
            response = requests.post(url, headers=headers, files={"filename": f})

        if response.status_code == 202:
            logging.info(response.json())
            import_id = response.json()["id"]
            logging.info(f"Uploading file uploading with id: {import_id}")
        else:
            self.force_raise_http_error(response)

        get_import_url = self.base_url + f"groups/{workspace_id}/imports/{import_id}"

        while True:
            response = requests.get(url=get_import_url, headers=self.headers)
            if response.status_code != 200:
                logging.error("Failed to upload file to workspace.")
                self.force_raise_http_error(response)

            if response.json()["importState"] == "Succeeded":
                logging.info(f"Successfully imported file to workspace {workspace_name}.")
                return
            else:
                logging.info("Import is currently in progress. . . Please wait.")

    @check_bearer_token
    def update_parameters_in_dataset(self, workspace_name: str, dataset_name: str, parameters: list):
        workspace_id, dataset_id = self.get_workspace_and_dataset_id(workspace_name, dataset_name)

        update_details = {"updateDetails": parameters}
        url = self.base_url + f"groups/{workspace_id}/datasets/{dataset_id}/UpdateParameters"
        headers = {"Content-Type": "application/json", **self.get_authz_header()}
        response = requests.post(url, json=update_details, headers=headers)

        if response.status_code == HTTP_OK_CODE:
            for parameter in parameters:
                logging.info(
                    f"Parameter \"{parameter['name']}\"",
                    f"updated to \"{parameter['newValue']}\"",
                    f"in dataset '{dataset_name}' in the '{workspace_name}' workspace.",
                )
        else:
            logging.error(f"Failed to update parameters for {dataset_name}.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def get_parameters_in_dataset(self, workspace_name: str, dataset_name: str) -> List:
        workspace_id, dataset_id = self.get_workspace_and_dataset_id(workspace_name, dataset_name)
        url = self.base_url + f"groups/{workspace_id}/datasets/{dataset_id}/parameters"
        response = requests.get(url, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully retrieved parameters for {dataset_name}.")
            return response.json()["value"]
        else:
            logging.error(f"Failed to retrieve parameters for dataset {dataset_name}.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def take_over_dataset(self, workspace_name: str, dataset_name: str) -> None:
        workspace_id, dataset_id = self.get_workspace_and_dataset_id(workspace_name, dataset_name)
        url = self.base_url + f"groups/{workspace_id}/datasets/{dataset_id}/TakeOver"
        response = requests.post(url, headers=self.headers)

        if response.status_code == HTTP_OK_CODE:
            logging.info(f"Successfully transferred ownership of {dataset_name} to this account.")
        else:
            logging.error(f"Failure to transfer ownership of {dataset_name} to this account.")
            self.force_raise_http_error(response)

    @check_bearer_token
    def get_dataset_refresh_history(self, workspace_name: str, dataset_name: str, top=10) -> List:
        workspace_id, dataset_id = self.get_workspace_and_dataset_id(workspace_name, dataset_name)

        url = self.base_url + f"groups/{workspace_id}/datasets/{dataset_id}/refreshes?$top={top}"

        response = requests.get(url, headers=self.headers)

        if response.status_code in [HTTP_OK_CODE, HTTP_CREATED_CODE, HTTP_ACCEPTED_CODE]:
            return response.json()["value"]
        else:
            logging.error(f"Failed getting refresh history for {dataset_name}.")
            self.force_raise_http_error(response)

    @staticmethod
    def force_raise_http_error(
        response: requests.Response, expected_codes: Union[List[int], int] = HTTP_OK_CODE
    ) -> NoReturn:
        logging.error(f"Expected response code(s) {expected_codes}, got {response.status_code}: {response.text}.")
        response.raise_for_status()
        raise requests.HTTPError(response)

    def get_workspace_and_dataset_id(self, workspace_name: str, dataset_name: str) -> Union:
        workspace_id = self.find_entity_id_by_name(self.workspaces, workspace_name, "workspace", raise_if_missing=True)
        datasets = self.get_datasets_in_workspace(workspace_name)
        dataset_id = self.find_entity_id_by_name(datasets, dataset_name, "dataset", raise_if_missing=True)
        return workspace_id, dataset_id