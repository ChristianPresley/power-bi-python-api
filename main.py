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

test = pbi_client.get_workspace('Testing Environment [Dev]')

print(test)
