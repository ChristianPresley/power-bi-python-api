#!/usr/bin/env python

import logging
import time

from pbi_rest_client.capacities import Capacities
from pbi_rest_client.rest_client import RestClient
from pbi_rest_client.workspaces import Workspaces
from pbi_rest_client.pipelines import Pipelines
from pbi_rest_client.dataflows import Dataflows

logging.basicConfig(level=logging.INFO)

client = RestClient()
capacities = Capacities(client)
workspaces = Workspaces(client)
pipelines = Pipelines(client)
dataflows = Dataflows(client)

print (workspaces.create_workspace('Testing Environment [Test]'))
print (capacities.set_workspace_capacity('Testing Environment [Test]', '4846741C-9AC0-456B-A0F2-6BA8C4D1D720'))
print (pipelines.create_pipeline('Testing Environment'))
print (pipelines.assign_pipeline_workspace('Testing Environment', 'Testing Environment [Test]', 'test'))
print (dataflows.delete_dataflow('Testing Environment [Test]', 'SQLDataFlow'))
time.sleep(10)
print (pipelines.pipeline_stage_deploy_selective('Testing Environment', 'promote', 'Dev'))
time.sleep(10)
