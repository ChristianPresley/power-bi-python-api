import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from keyvault import Utils

key_vault = Utils()

key_vault.get_keyvault_secret('appconfig')

print (key_vault.secret)

try:
    print("Azure App Configuration - Python Quickstart")
    # connection_string = key_vault.secret

    app_config_client.AzureAppConfigurationClient()
    # app_config_client = AzureAppConfigurationClient.from_connection_string(connection_string)
    test = app_config_client.list_configuration_settings(key_filter="workspace*")
    for item in test:
        print (item.key + item.value)
except Exception as ex:
    print('Exception:')
    print(ex)