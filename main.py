#!/usr/bin/env python

import logging
import json

from pbi_rest_client.capacities import Capacities
from pbi_rest_client.rest_client import RestClient
from pbi_rest_client.workspaces import Workspaces
from pbi_rest_client.pipelines import Pipelines
from pbi_rest_client.dataflows import Dataflows

logging.basicConfig(level=logging.INFO)

client = RestClient()
capacities = Capacities(client.authz_header, client.token, client.token_expiration)
workspaces = Workspaces(client.authz_header, client.token, client.token_expiration)
pipelines = Pipelines(client.authz_header, client.token, client.token_expiration)
dataflows = Dataflows(client.authz_header, client.token, client.token_expiration)

print (workspaces.create_workspace('Testing Environment [Dev]'))
print (workspaces.create_workspace('Testing Environment [Test]'))
print (workspaces.create_workspace('Testing Environment [Prod]'))

print (capacities.set_workspace_capacity('Testing Environment [Dev]', '4846741C-9AC0-456B-A0F2-6BA8C4D1D720'))
print (capacities.set_workspace_capacity('Testing Environment [Test]', '4846741C-9AC0-456B-A0F2-6BA8C4D1D720'))
print (capacities.set_workspace_capacity('Testing Environment [Prod]', '4846741C-9AC0-456B-A0F2-6BA8C4D1D720'))

print (pipelines.create_pipeline('Testing Environment'))
print (pipelines.assign_pipeline_workspace('Testing Environment', 'Testing Environment [Dev]', 'dev'))
print (pipelines.assign_pipeline_workspace('Testing Environment', 'Testing Environment [Test]', 'test'))
print (pipelines.assign_pipeline_workspace('Testing Environment', 'Testing Environment [Prod]', 'prod'))
# print (pipelines.pipeline_stage_deploy_all('Testing Environment', 'promote', 'Dev'))
print (pipelines.pipeline_stage_deploy_all('Testing Environment', 'promote', 'Test'))
# print (pipelines.pipeline_stage_deploy_dataflow('Testing Environment', 'Test'))

print (dataflows.get_dataflows('Testing Environment [Dev]'))
print (dataflows.get_dataflow('Testing Environment [Test]', 'FirstLast'))

# print (imports.import_file_into_workspace('Testing Environment [Dev]', False, 'SharePointListDemo.pbix', 'SharePointListDemo'))
# print (imports.import_file_into_workspace('Testing Environment [Dev]', False, 'FirstLast.json', 'SharePointListDemo'))