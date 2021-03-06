#!/usr/bin/env python

import logging
import requests

from typing import List
from .utils.utils import Utils
from .workspaces import Workspaces
from .dataflows import Dataflows
from .datasets import Datasets
from .dashboards import Dashboards
from .reports import Reports

utils = Utils()

class Pipelines:
    def __init__(self, client):
        self.client = client
        self.workspaces = Workspaces(client)
        self.dataflows = Dataflows(client)
        self.datasets = Datasets(client)
        self.dashboards = Dashboards(client)
        self.reports = Reports(client)
        self.pipelines = None
        self.pipeline = {}
        self._stage_deploy_is_backwards = False
        self.pipeline_stage_order = None
        self.pipeline_stage = None
        self.pipeline_target_stage = None
        self._workspace_keys = utils.get_appconfig_keys(key_filter = 'workspace-name*')
        self.pipeline_stages = {'dev': 0, 'test': 1, 'prod': 2}
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/pipelines/get-pipeline
    def get_pipeline(self, pipeline_name: str) -> List:
        self.client.check_token_expiration()
        self.get_pipeline_id(pipeline_name)

        url = self.client.base_url + "pipelines/" + self.pipeline[pipeline_name] + "?$expand=stages"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved pipeline {self.pipeline[pipeline_name]}.")
            return response.json()
        else:
            logging.error(f"Failed to retrieve pipeline {self.pipeline[pipeline_name]}.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/pipelines/get-pipelines
    def get_pipelines(self) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "pipelines"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved pipelines.")
            self.pipelines = response.json()["value"]
            return self.pipelines
        else:
            logging.error("Failed to retrieve pipelines.")
            self.client.force_raise_http_error(response)
    
    def get_pipeline_id(self, pipeline_name: str) -> str:
        self.client.check_token_expiration()
        pipeline_missing = True

        self.get_pipelines()
        
        for item in self.pipelines:
            if item['displayName'] == pipeline_name:
                logging.info(f"Found pipeline with name {pipeline_name} and pipeline id {item['id']}.")
                self.pipeline = {pipeline_name: item['id']}
                pipeline_missing = False
                return self.pipeline
        if pipeline_missing:
            raise RuntimeError(f"Unable to find pipeline with name: '{pipeline_name}'")

    def validate_pipeline_stage(self, stage: str):
        stage = stage.lower()
        
        if stage in self.pipeline_stages:
            logging.info(f"Pipeline stage order is set to {stage}.")
            self.pipeline_stage_order = self.pipeline_stages[stage]
            self.pipeline_stage = stage
            return self.pipeline_stage_order
        else:
            raise Exception(f"Incorrect stage specified. Available options are: {list(self.pipeline_stages.keys())}")

    # https://docs.microsoft.com/en-us/rest/api/power-bi/pipelines/get-pipeline-stages
    def get_pipeline_stage_assignment(self, pipeline_name: str, workspace_name: str, stage: str) -> List:
        self.client.check_token_expiration()
        self.get_pipeline_id(pipeline_name)
        self.workspaces.get_workspace_id(workspace_name)
        self.validate_pipeline_stage(stage)

        url = self.client.base_url + "pipelines/" + self.pipeline[pipeline_name] + "/stages"
                
        response = requests.get(url, headers = self.client.json_headers)
                   
        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved pipeline stages for pipeline {pipeline_name}.")
            for object in response.json()["value"]:
                if object["order"] == self.pipeline_stage_order:
                    if "workspaceId" in object:
                        assignment_workspace_id = object["workspaceId"]
                        if assignment_workspace_id == self.workspaces.workspace[workspace_name]:
                            logging.info(f"Pipeline stage assignment for {pipeline_name} already exists.")
                            return True
                        elif assignment_workspace_id != self.workspaces.workspace[workspace_name]:
                            raise Exception(f"Pipeline stage assignment for {pipeline_name} already exists, but with incorrect workspace id {assignment_workspace_id}.")
                    elif "workspaceId" not in object:
                        logging.info(f"Pipeline stage assignment for {pipeline_name} does not exist.")
                        return False
        else:
            logging.error(f"Failed to retrieve pipeline stages for pipeline {pipeline_name}.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/pipelines/create-pipeline
    def create_pipeline(self, pipeline_name: str) -> None:
        self.client.check_token_expiration()
        self.get_pipelines()
        self.pipeline_exists = False
               
        for object in self.pipelines:
            if object['displayName'] == f'{pipeline_name}':
                logging.info(f"Successfully retrieved pipeline with name {pipeline_name}.")
                self.pipeline_exists = True
                break

        if self.pipeline_exists:
            logging.warning(f"Pipeline {pipeline_name} already exists, no changes made.")
            return

        logging.info(f"Attempting to create pipeline with name: {pipeline_name}...")
        url = self.client.base_url + "pipelines"
        
        response = requests.post(url, data={"displayName": pipeline_name}, headers=self.client.url_encoded_headers)

        if response.status_code == self.client.http_created_code:
            logging.info(f"Successfully created pipeline {pipeline_name}.")
            self.get_pipelines()
            return response.json()
        else:
            logging.error(f"Failed to create the new pipeline: '{pipeline_name}':")
            self.client.force_raise_http_error(response)

    # https://docs.microsoft.com/en-us/rest/api/power-bi/pipelines/assign-workspace
    def assign_pipeline_workspace(self, pipeline_name: str, workspace_name: str, stage: str) -> None:
        self.client.check_token_expiration()
        stage_assigned = self.get_pipeline_stage_assignment(pipeline_name, workspace_name, stage)
        
        if stage_assigned == True:
            logging.info(f"Pipeline stage: '{self.pipeline_stage}' in pipeline: '{pipeline_name}' is already assigned to workspace: {self.workspaces.workspace}.")
            return "Pipeline stage already assigned."
        
        if stage_assigned == False:
            logging.info(f"Pipeline stage: '{self.pipeline_stage}' in pipeline: '{pipeline_name}' is not assigned to workspace: {self.workspaces.workspace}. Proceeding to assign pipeline stage.")

            url = self.client.base_url + "pipelines/" + self.pipeline[pipeline_name] + f"/stages/{self.pipeline_stage_order}/assignWorkspace"

            request_payload = {
                'workspaceId': self.workspaces.workspace[workspace_name]
            }

            response = requests.post(url, data = request_payload, headers = self.client.url_encoded_headers)

            if response.status_code == self.client.http_ok_code:
                logging.info(f"Successfully assigned workspace with ID {self.workspaces.workspace[workspace_name]} to pipeline {pipeline_name}.")
                return f"Pipeline stage assigned successfully with URI: {response.request.url}"
            else:
                logging.error(f"Failed to assign workspace with ID {self.workspaces.workspace[workspace_name]} to pipeline {pipeline_name}.")
                self.client.force_raise_http_error(response)

    def pipeline_stage_selector(self, type: str, stage: str):
        self.validate_pipeline_stage(stage)

        if type != 'promote' and type != 'demote':
            raise Exception("Incorrect pipeline stage deployment type specified. Valid options are: 'promote' and 'demote'")

        if type == 'promote':
            if self.pipeline_stage_order < 2:
                self.pipeline_target_stage = self.pipeline_stage_order + 1
            elif self.pipeline_stage_order >= 2:
                raise Exception("Production is the highest stage in Power BI pipeline. You cannot promote Production to another stage.")
        
        if type == 'demote':
            if self.pipeline_stage_order > 0:
                self.pipeline_target_stage = self.pipeline_stage_order - 1
                self._stage_deploy_is_backwards = True
            elif self.pipeline_stage_order <= 0:
                raise Exception("Development is the lowest stage in Power BI pipeline. You cannot demote Development to another stage.")
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/pipelines/deploy-all
    def pipeline_stage_deploy_all(self, pipeline_name: str, type: str, stage: str) -> None:
        self.client.check_token_expiration()
        self.get_pipeline_id(pipeline_name)
        self.pipeline_stage_selector(type, stage)
        
        request_url = self.client.base_url + "pipelines/" + self.pipeline[pipeline_name] + "/deployAll"

        request_payload = {
            'sourceStageOrder': self.pipeline_stage_order,
            'isBackwardDeployment': self._stage_deploy_is_backwards,
            'options': {
                'allowCreateArtifact': True,
                'allowOverwriteArtifact': True,
                'allowOverwriteTargetArtifactLabel': True,
                'allowPurgeData': True,
                'allowSkipTilesWithMissingPrerequisites': True,
                'allowTakeOver': True
            }
        }
        
        response = requests.post(request_url, json = request_payload, headers = self.client.json_headers)
        
        if response.status_code == self.client.http_accepted_code:
            logging.info(f"Successfully promoted stage: '{self.pipeline_stage}' in pipeline: '{pipeline_name}' to stage: '{list(self.pipeline_stages)[self.pipeline_target_stage]}'.")
            return response
        else:
            logging.error(f"Failed to promote stage: '{self.pipeline_stage}' in pipeline: '{pipeline_name}' to stage: '{list(self.pipeline_stages)[self.pipeline_target_stage]}'.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/pipelines/selective-deploy
    def pipeline_stage_deploy_selective(self, pipeline_name: str, type: str, stage: str) -> None:
        self.client.check_token_expiration()
        self.get_pipeline_id(pipeline_name)
        self.pipeline_stage_selector(type, stage)
        workspace_name = self._workspace_keys[f'workspace-name-{self.pipeline_stage}']
        deploy_dataflows = utils.get_appconfig_feature_flags('dataflows')['enabled']
        deploy_datasets = utils.get_appconfig_feature_flags('datasets')['enabled']
        deploy_reports = utils.get_appconfig_feature_flags('reports')['enabled']
        deploy_dashboards = utils.get_appconfig_feature_flags('dashboards')['enabled']
        dataflow_list = []
        dataset_list = []
        report_list = []
        dashboard_list = []

        if deploy_dataflows:
            self.dataflows.get_dataflows(workspace_name)
            for item in self.dataflows.dataflows:
                dataflow_list.append({"sourceId": f"{item['objectId']}"})

        if deploy_datasets or deploy_reports:
            if deploy_reports and not deploy_datasets:
                self.reports.get_reports(workspace_name)
                for item in self.reports.reports:
                    report_list.append({"sourceId": f"{item['id']}"})
                    dataset_list.append({"sourceId": f"{item['datasetId']}"})
            elif not deploy_reports and deploy_datasets:
                self.datasets.get_datasets_in_workspace(workspace_name)
                for item in self.datasets.datasets:
                    dataset_list.append({"sourceId": f"{item['id']}"})
            else:
                self.reports.get_reports(workspace_name)
                self.datasets.get_datasets_in_workspace(workspace_name)
                for item in self.reports.reports:
                    report_list.append({"sourceId": f"{item['id']}"})
                for item in self.datasets.datasets:
                    dataset_list.append({"sourceId": f"{item['id']}"})

        if deploy_dashboards:
            self.dashboards.get_dashboards(workspace_name)
            for item in self.dashboards.dashboards:
                dashboard_list.append({"sourceId": f"{item['id']}"})

        request_url = self.client.base_url + "pipelines/" + self.pipeline[pipeline_name] + "/deploy"

        request_payload = {
            "sourceStageOrder": self.pipeline_stage_order,
            'isBackwardDeployment': self._stage_deploy_is_backwards,
            "dataflows": dataflow_list,
            "datasets": dataset_list,
            "reports": report_list,
            "dashboards": dashboard_list,
            'options': {
                'allowCreateArtifact': True,
                'allowOverwriteArtifact': True,
                'allowOverwriteTargetArtifactLabel': True,
                'allowPurgeData': True,
                'allowSkipTilesWithMissingPrerequisites': True,
                'allowTakeOver': True
            }
        }
        
        response = requests.post(request_url, json = request_payload, headers = self.client.json_headers)
        
        if response.status_code == self.client.http_accepted_code:
            logging.info(f"Successfully promoted stage: '{self.pipeline_stage}' in pipeline: '{pipeline_name}' to stage: '{list(self.pipeline_stages)[self.pipeline_target_stage]}'.")
            return response
        else:
            logging.error(f"Failed to promote stage: '{self.pipeline_stage}' in pipeline: '{pipeline_name}' to stage: '{list(self.pipeline_stages)[self.pipeline_target_stage]}'.")
            self.client.force_raise_http_error(response)
    
    # https://docs.microsoft.com/en-us/rest/api/power-bi/pipelines/update-pipeline-user
    def add_user_to_pipeline(self, pipeline_name: str, principal_id: str, access_right: str, service_principal: bool, group: bool, user_account: bool) -> bool:
        self.client.check_token_expiration()
        self.get_pipeline_id(pipeline_name)

        url = self.client.base_url + "pipelines/" + self.pipeline[pipeline_name] + "/users"

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
            "accessRight": access_right,
            "principalType": principal_type
        }

        response = requests.post(url, json = request_payload, headers = self.client.json_headers)
                   
        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully assigned user to pipeline: {pipeline_name}.")
            return True
        else:
            logging.error(f"Failed to assign user to pipeline: {pipeline_name}.")
            self.client.force_raise_http_error(response)