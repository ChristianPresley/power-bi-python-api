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

deploy_pipeline_test = pbi_client.deploy_all_pipeline_stage('Testing Environment', 'Testing Environment [Test]', '4846741C-9AC0-456B-A0F2-6BA8C4D1D720', "Dev")
time.sleep(5)
deploy_pipeline_prod = pbi_client.deploy_all_pipeline_stage('Testing Environment', 'Testing Environment [Prod]', '4846741C-9AC0-456B-A0F2-6BA8C4D1D720', "Test")
time.sleep(5)