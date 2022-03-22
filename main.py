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

json_object = pbi_client.add_user_to_pipeline('MyTest', {"identifier": "admin@M365x51939963.onmicrosoft.com", "pipelineUserAccessRight": "Admin", "principalType": "User"})

print (json_object)
