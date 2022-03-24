import logging
import json
import secrets

from power_bi_api_client import PowerBIAPIClient

pbi_client = PowerBIAPIClient(
    secrets.tenant_id,
    secrets.client_id,
    secrets.client_secret,
)

logging.basicConfig(level=logging.INFO)

create_workspace = pbi_client.create_workspace('Testing Environment')
import_pbix_file = pbi_client.import_file_into_workspace('Testing Environment', False, 'SharePointListDemo.pbix', 'SharePointListDemo')
create_pipeline = pbi_client.create_pipeline('Testing Environment')
add_user_workspace = pbi_client.add_user_to_workspace('Testing Environment', {"identifier": "admin@M365x51939963.onmicrosoft.com", "userAccessRight": "Admin", "principalType": "User"})
add_user_pipeline = pbi_client.add_user_to_pipeline('Testing Environment', {"identifier": "admin@M365x51939963.onmicrosoft.com", "pipelineUserAccessRight": "Admin", "principalType": "User"})

print (create_workspace)
print (import_pbix_file)
print (create_pipeline)
print (add_user_workspace)
print (add_user_pipeline)
