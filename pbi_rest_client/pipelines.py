#!/usr/bin/env python

import logging
import datetime
from tabnanny import check
import requests

from typing import List
from urllib import parse

from .rest_client import RestClient
from .workspaces import Workspaces

class Pipelines:
    def __init__(self, authz_header = None, token = None, token_expiration = None):
        self.client = RestClient(authz_header, token, token_expiration)
        self.workspaces = Workspaces(authz_header, token, token_expiration)
        self._pipelines = None
        self._pipeline = {}
        self._pipeline_stage_order = None
        self._pipeline_stage = None
        self.pipeline_stages = {'DEV': 0, 'TEST': 1, 'PROD': 2}
        
    def get_pipeline(self, pipeline_name: str) -> List:
        self.client.check_token_expiration()
        self.get_pipeline_id(pipeline_name)

        url = self.client.base_url + "pipelines/" + self._pipeline[pipeline_name] + "?$expand=stages"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved pipeline {self._pipeline[pipeline_name]}.")
            return response.json()
        else:
            logging.error(f"Failed to retrieve pipeline {self._pipeline[pipeline_name]}.")
            self.force_raise_http_error(response)
    
    def get_pipelines(self) -> List:
        self.client.check_token_expiration()

        url = self.client.base_url + "pipelines"
        
        response = requests.get(url, headers = self.client.json_headers)

        if response.status_code == self.client.http_ok_code:
            logging.info("Successfully retrieved pipelines.")
            self._pipelines = response.json()["value"]
            return self._pipelines
        else:
            logging.error("Failed to retrieve pipelines.")
            self.force_raise_http_error(response)
       
    def get_pipeline_id(self, pipeline_name: str) -> str:
        self.client.check_token_expiration()
        pipeline_missing = True

        self.get_pipelines()
        
        for item in self._pipelines:
            if item['displayName'] == pipeline_name:
                logging.info(f"Found pipeline with name {pipeline_name} and pipeline id {item['id']}.")
                self._pipeline = {pipeline_name: item['id']}
                pipeline_missing = False
                return self._pipeline
        if pipeline_missing:
            raise RuntimeError(f"Unable to find pipeline with name: '{pipeline_name}'")

    def validate_pipeline_stage(self, stage: str):
        stage = stage.upper()
        
        if stage in self.pipeline_stages:
            logging.info(f"Pipeline stage order is set to {stage}.")
            self._pipeline_stage_order = self.pipeline_stages[stage]
            self._pipeline_stage = stage
            return self._pipeline_stage_order
        else:
            raise Exception(f"Incorrect stage specified. Available options are: {list(self.pipeline_stages.keys())}")

    def get_pipeline_stage_assignment(self, pipeline_name: str, workspace_name: str, stage: str) -> List:
        self.client.check_token_expiration()
        self.get_pipeline_id(pipeline_name)
        self.workspaces.get_workspace_id(workspace_name)
        self.validate_pipeline_stage(stage)

        url = self.client.base_url + "pipelines/" + self._pipeline[pipeline_name] + "/stages"
                
        response = requests.get(url, headers = self.client.json_headers)
                   
        if response.status_code == self.client.http_ok_code:
            logging.info(f"Successfully retrieved pipeline stages for pipeline {pipeline_name}.")
            for object in response.json()["value"]:
                if object["order"] == self._pipeline_stage_order:
                    if "workspaceId" in object:
                        assignment_workspace_id = object["workspaceId"]
                        if assignment_workspace_id == self.workspaces._workspace[workspace_name]:
                            logging.info(f"Pipeline stage assignment for {pipeline_name} already exists.")
                            return True
                        elif assignment_workspace_id != self.workspaces._workspace[workspace_name]:
                            raise Exception(f"Pipeline stage assignment for {pipeline_name} already exists, but with incorrect workspace id {assignment_workspace_id}.")
                    elif "workspaceId" not in object:
                        logging.info(f"Pipeline stage assignment for {pipeline_name} does not exist.")
                        return False
        else:
            logging.error(f"Failed to retrieve pipeline stages for pipeline {pipeline_name}.")
            self.force_raise_http_error(response)
    
    def create_pipeline(self, pipeline_name: str) -> None:
        self.client.check_token_expiration()
        self.get_pipelines()
        self.pipeline_exists = False
               
        for object in self._pipelines:
            if object['displayName'] == f'{pipeline_name}':
                logging.info(f"Successfully retrieved pipeline with name {pipeline_name}.")
                self.pipeline_exists = True
                break

        if self.pipeline_exists:
            logging.warning(f"Pipeline {pipeline_name} already exists, no changes made.")
            return

        logging.info(f"Attempting to create pipeline with name: {pipeline_name}...")
        url = self.base_url + "pipelines"
        
        response = requests.post(url, data={"displayName": pipeline_name}, headers=self.headers)

        if response.status_code == self.client.http_created_code:
            logging.info(f"Successfully created pipeline {pipeline_name}.")
            self.get_pipelines()
            return response.json()
        else:
            logging.error(f"Failed to create the new pipeline: '{pipeline_name}':")
            self.force_raise_http_error(response)

    def assign_pipeline_workspace(self, pipeline_name: str, workspace_name: str, stage: str) -> None:
        self.client.check_token_expiration()
        stage_assigned = self.get_pipeline_stage_assignment(pipeline_name, workspace_name, stage)
        
        if stage_assigned == True:
            logging.info(f"Pipeline stage: '{self._pipeline_stage}' in pipeline: '{pipeline_name}' is already assigned to workspace: {self.workspaces._workspace}.")
            return "Pipeline stage already assigned."
        
        if stage_assigned == False:
            logging.info(f"Pipeline stage: '{self._pipeline_stage}' in pipeline: '{pipeline_name}' is not assigned to workspace: {self.workspaces._workspace}. Proceeding to assign pipeline stage.")

            url = self.client.base_url + "pipelines/" + self._pipeline[pipeline_name] + f"/stages/{self._pipeline_stage_order}/assignWorkspace"

            request_payload = {
                'workspaceId': self.workspaces._workspace[workspace_name]
            }

            response = requests.post(url, data = request_payload, headers = self.client.urlencoded_headers)

            if response.status_code == self.client.http_ok_code:
                logging.info(f"Successfully assigned workspace with ID {self.workspaces._workspace[workspace_name]} to pipeline {pipeline_name}.")
                return f"Pipeline stage assigned successfully with URI: {response.request.url}"
            else:
                logging.error(f"Failed to assign workspace with ID {self.workspaces._workspace[workspace_name]} to pipeline {pipeline_name}.")
                self.force_raise_http_error(response)
    
    def pipeline_stage_deploy_all(self, pipeline_name: str, type: str, stage: str) -> None:
        self.client.check_token_expiration()
        self.get_pipeline_id(pipeline_name)
        self.validate_pipeline_stage(stage)
        is_backwards = False
        
        request_url = self.client.base_url + "pipelines/" + self._pipeline[pipeline_name] + "/deployAll"
        
        if type != 'promote' and type != 'demote':
            raise Exception("Incorrect pipeline stage deployment type specified. Valid options are: 'promote' and 'demote'")

        if type == 'promote':
            if self._pipeline_stage_order < 2:
                target_stage = self._pipeline_stage_order + 1
            elif self._pipeline_stage_order >= 2:
                raise Exception("Production is the highest stage in Power BI pipeline. You cannot promote Production to another stage.")
        
        if type == 'demote':
            if self._pipeline_stage_order > 0:
                target_stage = self._pipeline_stage_order - 1
                is_backwards = True
            elif self._pipeline_stage_order <= 0:
                raise Exception("Development is the lowest stage in Power BI pipeline. You cannot demote Development to another stage.")

        request_payload = {
            'sourceStageOrder': self._pipeline_stage_order,
            'isBackwardDeployment': is_backwards,
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
            logging.info(f"Successfully promoted stage: '{self._pipeline_stage}' in pipeline: '{pipeline_name}' to stage: '{list(self.pipeline_stages)[target_stage]}'.")
            return response
        else:
            # logging.error(f"Failed to promote stage {source_stage} in pipeline {pipeline_name} to {target_stage}.")
            self.force_raise_http_error(response)
    
    def pipeline_stage_deploy_dataflow(self, pipeline_name: str, stage: str) -> None:
        self.client.check_token_expiration()
        self.get_pipeline_id(pipeline_name)
        self.validate_pipeline_stage(stage)
        
        request_url = self.client.base_url + "pipelines/" + self._pipeline[pipeline_name] + "/deploy"
        
        request_payload = {
            "sourceStageOrder": "0",
            "dataflows": 
                [{
                  "sourceId": "23036473-9ba0-4757-ae49-04dd39977d76"
                }],
            "options": {
                "allowOverwriteArtifact": True,
                "allowCreateArtifact": True
            }
}
        
        response = requests.post(request_url, json = request_payload, headers = self.client.json_headers)
        
        if response.status_code == self.client.http_accepted_code:
            # logging.info(f"Successfully promoted stage: '{self._pipeline_stage}' in pipeline: '{pipeline_name}' to stage: '{list(self.pipeline_stages)[target_stage]}'.")
            return response
        else:
            # logging.error(f"Failed to promote stage {source_stage} in pipeline {pipeline_name} to {target_stage}.")
            self.force_raise_http_error(response)