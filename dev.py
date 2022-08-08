#!/usr/bin/env python

import logging
import time

# from pbi_rest_client.capacities import Capacities
from pbi_rest_client.datasets import Datasets
from pbi_rest_client.rest_client import RestClient
from pbi_rest_client.workspaces import Workspaces
# from pbi_rest_client.pipelines import Pipelines
# from pbi_rest_client.dataflows import Dataflows
# from pbi_rest_client.imports import Imports

logging.basicConfig(level=logging.INFO)

client = RestClient()
# capacities = Capacities(client)
workspaces = Workspaces(client)
datasets = Datasets(client)
# pipelines = Pipelines(client)
# dataflows = Dataflows(client)
# imports = Imports(client)

# print (workspaces.create_workspace('Testing Environment [Dev]'))
# print (capacities.set_workspace_capacity('Testing Environment [Dev]', '4846741C-9AC0-456B-A0F2-6BA8C4D1D720'))
# print (pipelines.create_pipeline('Testing Environment'))
# print (pipelines.assign_pipeline_workspace('Testing Environment', 'Testing Environment [Dev]', 'dev'))
# time.sleep(10)
# print (imports.import_file_into_workspace('Testing Environment [Dev]', 'SQLTableDemo', 'SQLTableDemo.pbix', restore_from_blob = True, blob_container_name = 'test-container', dataflow = False, skip_report = False))
# print (imports.import_file_into_workspace('Testing Environment [Dev]', 'SQLDataFlow', 'SQLDataFlow.json', restore_from_blob = False, blob_container_name = None, dataflow = True))

# print(datasets.get_dataset_refresh_history('SQLTableDemo', 'Testing Environment [Dev]))
# datasets.enhance_refresh_dataset('SQLTableDemo', 'Testing Environment [Dev], 'Automatic')
# time.sleep(10)
# print(datasets.get_dataset_refresh_history('SQLTableDemo', 'Testing Environment [Dev]',5) )
# time.sleep(2)
# datasets.cancel_dataset_refresh('SQLTableDemo', 'Testing Environment [Dev]')
# print(datasets.get_dataset_gateways('SQLTableDemo', 'Testing Environment [Dev]'))
print( datasets.get_user_in_dataset_id('SQLTableDemo', 'Testing Environment [Dev]', 'test@test.com') )
