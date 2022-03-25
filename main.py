import logging
import json
import time
import secrets

from power_bi_api_client import PowerBIAPIClient

pbi_client = PowerBIAPIClient(
    secrets.tenant_id,
    secrets.client_id,
    secrets.client_secret,
)

logging.basicConfig(level=logging.INFO)

test = pbi_client.get_pipeline("4d822c28-aa8e-46d4-b40c-a741714d28bc")
test1 = pbi_client.add_user_to_pipeline_by_id("4d822c28-aa8e-46d4-b40c-a741714d28bc", {"identifier": "admin@M365x51939963.onmicrosoft.com", "pipelineUserAccessRight": "Admin", "principalType": "User"})
test2 = pbi_client.add_user_to_pipeline_by_id("4d822c28-aa8e-46d4-b40c-a741714d28bc", {"identifier": "4106f761-3b6c-4099-849e-31fbd638ffb0", "pipelineUserAccessRight": "Admin", "principalType": "App"})

print(test)
print(test1)
print(test2)