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

dev_workspace_capacity = "4846741C-9AC0-456B-A0F2-6BA8C4D1D720"
test_workspace_capacity = "4846741C-9AC0-456B-A0F2-6BA8C4D1D720"
prod_workspace_capacity = "4846741C-9AC0-456B-A0F2-6BA8C4D1D720"

check_workspace_dev = pbi_client.get_workspace('Testing Environment [Dev]')

if check_workspace_dev == 0:
    create_workspace_dev = pbi_client.create_workspace('Testing Environment [Dev]')
    time.sleep(5)
    set_workspace_capacity = pbi_client.set_workspace_capacity('Testing Environment [Dev]', {"capacityId": {dev_workspace_capacity}})
    time.sleep(5)
    add_user_workspace_dev = pbi_client.add_user_to_workspace('Testing Environment [Dev]', {"identifier": "admin@M365x51939963.onmicrosoft.com", "groupUserAccessRight": "Admin", "principalType": "User"})
    time.sleep(5)
    import_pbix_file = pbi_client.import_file_into_workspace('Testing Environment [Dev]', False, 'SharePointListDemo.pbix', 'SharePointListDemo')
    time.sleep(5)
else:
    logging.info('Dev workspace already exists.')

check_workspace_test = pbi_client.get_workspace('Testing Environment [Test]')

if check_workspace_test == 0:
    create_workspace_test = pbi_client.create_workspace('Testing Environment [Test]')
    time.sleep(5)
    set_workspace_capacity_test = pbi_client.set_workspace_capacity('Testing Environment [Test]', {"capacityId": {test_workspace_capacity}})
    time.sleep(5)
    add_user_workspace_test = pbi_client.add_user_to_workspace('Testing Environment [Test]', {"identifier": "admin@M365x51939963.onmicrosoft.com", "groupUserAccessRight": "Admin", "principalType": "User"})
    time.sleep(5)
    # import_pbix_file_test = pbi_client.import_file_into_workspace('Testing Environment [Test]', False, 'SharePointListDemo.pbix', 'SharePointListDemo')
    # time.sleep(5)
else:
    logging.info('Test workspace already exists.')

check_workspace_prod = pbi_client.get_workspace('Testing Environment [Prod]')

if check_workspace_prod == 0:
    create_workspace_prod = pbi_client.create_workspace('Testing Environment [Prod]')
    time.sleep(5)
    set_workspace_capacity_prod = pbi_client.set_workspace_capacity('Testing Environment [Prod]', {"capacityId": {prod_workspace_capacity}})
    time.sleep(5)
    add_user_workspace_prod = pbi_client.add_user_to_workspace('Testing Environment [Prod]', {"identifier": "admin@M365x51939963.onmicrosoft.com", "groupUserAccessRight": "Admin", "principalType": "User"})
    time.sleep(5)
    # import_pbix_file_prod = pbi_client.import_file_into_workspace('Testing Environment [Prod]', False, 'SharePointListDemo.pbix', 'SharePointListDemo')
    # time.sleep(5)
else:
    logging.info('Prod workspace already exists.')
