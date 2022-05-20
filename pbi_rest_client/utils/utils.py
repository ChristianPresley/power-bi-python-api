#!/usr/bin/env python

import logging

from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobClient
from azure.keyvault.secrets import SecretClient
from azure.appconfiguration import AzureAppConfigurationClient, FeatureFlagConfigurationSetting
from ..config import BaseConfig

config = BaseConfig()

class Utils:
    storage_account_credential = ClientSecretCredential(config.STORAGE_ACCOUNT_TENANT_ID, config.STORAGE_ACCOUNT_CLIENT_ID, config.STORAGE_ACCOUNT_CLIENT_SECRET)
    app_config_credential = ClientSecretCredential(config.APP_CONFIG_TENANT_ID, config.APP_CONFIG_CLIENT_ID, config.APP_CONFIG_CLIENT_SECRET)
    key_vault_credential = ClientSecretCredential(config.KEY_VAULT_TENANT_ID, config.KEY_VAULT_CLIENT_ID, config.KEY_VAULT_CLIENT_SECRET)

    def __init__(self) -> None:
        self.app_config_client = AzureAppConfigurationClient(base_url = config.APP_CONFIG_URI, credential = Utils.app_config_credential)
        self.key_vault_secret_client = SecretClient(vault_url = config.KEY_VAULT_URI, credential = Utils.key_vault_credential)
        self.secret = None
        self.workspaces = {}
        self.feature_flags = {}
        self.auth_mode = self.get_appconfig_feature_flags('service-account')['enabled']

    def get_keyvault_secret(self, secret_name: str)  -> None:
        logging.info(f"Retrieving your secret from {config.KEY_VAULT_NAME}.")

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
    
    def blob_client(self, blob_name: str):
        blob_client = BlobClient(
            account_url = config.STORAGE_ACCOUNT_URI,
            container_name = config.STORAGE_BLOB_CONTAINER_NAME,
            blob_name = blob_name,
            credential = Utils.storage_account_credential
        )

        return blob_client