#!/usr/bin/env python

import os
import logging

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.appconfiguration import AzureAppConfigurationClient, FeatureFlagConfigurationSetting

class Utils:
    key_vault_tenant_id = os.environ['KEYVAULT_TENANT_ID']
    key_vault_client_id = os.environ['KEYVAULT_CLIENT_ID']
    key_vault_client_secret = os.environ['KEYVAULT_CLIENT_SECRET']
    app_config_name = os.environ['APPCONFIG_NAME']
    app_config_uri = f"https://{app_config_name}.azconfig.io"
    key_vault_name = os.environ['KEYVAULT_NAME']
    key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
    credential = ClientSecretCredential(key_vault_tenant_id, key_vault_client_id, key_vault_client_secret)

    def __init__(self) -> None:
        self.app_config_client = AzureAppConfigurationClient(Utils.app_config_uri, Utils.credential)
        self.key_vault_secret_client = SecretClient(vault_url = Utils.key_vault_uri, credential = Utils.credential)
        self.app_config_name = Utils.app_config_name
        self.key_vault_name = Utils.key_vault_name
        self.secret = None
        self.workspaces = {}
        self.feature_flags = {}
        self.auth_mode = self.get_appconfig_feature_flags('service-account')['enabled']

    def get_keyvault_secret(self, secret_name: str)  -> None:
        logging.info(f"Retrieving your secret from {self.key_vault_name}.")

        retrieved_secret = self.key_vault_secret_client.get_secret(secret_name)
        self.secret = retrieved_secret.value
    
    def get_appconfig_keys(self, **kwargs) -> None:
        key_filter = kwargs.get('key_filter', None)

        if key_filter != None:
            list_keys = self.app_config_client.list_configuration_settings(key_filter=key_filter)
        else:
            list_keys = self.app_config_client.list_configuration_settings()
        
        for item in list_keys:
            self.workspaces[item.key] = item.value
        
        return self.workspaces

    def get_appconfig_feature_flags(self, feature_flag_name: str) -> None:
        feature_flag_config_setting = FeatureFlagConfigurationSetting(feature_id = feature_flag_name)
        feature_flag = self.app_config_client.get_configuration_setting(feature_flag_config_setting.key)

        self.feature_flags['key'] = feature_flag.key
        self.feature_flags['feature_id'] = feature_flag.feature_id
        self.feature_flags['enabled'] = feature_flag.enabled
        self.feature_flags['kind'] = feature_flag.kind
        
        return self.feature_flags