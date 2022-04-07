#!/usr/bin/env python

import logging

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

# print (workspaces.get_workspace('Testing Environment [Dev]'))
# print (workspaces.create_workspace('Testing Environment [QA]'))

# for object in workspaces.get_workspaces():
#     print (object)

# print (workspaces.get_workspace_id('Testing Environment [Prod]'))

# print (capacities.set_workspace_capacity('testworkspace', '4846741C-9AC0-456B-A0F2-6BA8C4D1D720'))
# print (capacities.set_workspace_capacity('testworkspace', '00000000-0000-0000-0000-000000000000'))

# print (pipelines.get_pipelines())
# print (pipelines.get_pipeline_id('Demo Pipeline'))
# print (pipelines.get_pipeline('Testing Environment'))
# print (pipelines.assign_pipeline_workspace('Testing Environment', 'Testing Environment [Test]', 'dev'))
# print (pipelines.pipeline_stage_deploy_all('Testing Environment', 'demote', 'Test'))
print (pipelines.pipeline_stage_deploy_dataflow('Testing Environment', 'Test'))

# print (dataflows.get_dataflows('Testing Environment [Dev]'))
# print (dataflows.get_dataflow('Testing Environment [Dev]', 'FirstLast'))