import enum
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


deploy_pipeline_prod = pbi_client.deploy_all_pipeline_stage('Testing Environment', "Test")