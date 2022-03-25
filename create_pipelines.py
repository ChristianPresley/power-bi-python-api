import logging
import time
import secrets

from power_bi_api_client import PowerBIAPIClient

pbi_client = PowerBIAPIClient(
    secrets.tenant_id,
    secrets.client_id,
    secrets.client_secret,
)

logging.basicConfig(level=logging.INFO)

create_pipeline_dev = pbi_client.create_pipeline('Testing Environment')
time.sleep(15)
add_user_pipeline_dev = pbi_client.add_user_to_pipeline('Testing Environment', {"identifier": "admin@M365x51939963.onmicrosoft.com", "pipelineUserAccessRight": "Admin", "principalType": "User"})
time.sleep(5)
assign_pipeline_workspace_dev = pbi_client.assign_pipeline_workspace('Testing Environment', 'Testing Environment [Dev]', 0)
time.sleep(5)
assign_pipeline_workspace_test = pbi_client.assign_pipeline_workspace('Testing Environment', 'Testing Environment [Test]', 1)
time.sleep(5)
assign_pipeline_workspace_prod = pbi_client.assign_pipeline_workspace('Testing Environment', 'Testing Environment [Prod]', 2)
time.sleep(5)