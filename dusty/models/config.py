#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011,R0903,R0201,E0401,W0702,C0411

#   Copyright 2019 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
    Config helper
"""

import os
import re
import yaml
import hvac
import minio
import urllib3

from ruamel.yaml.comments import CommentedMap

from dusty.tools.dict import recursive_merge
from dusty.tools import log
from dusty import constants


class ConfigModel:
    """ Parses config """

    def __init__(self, context):
        """ Initialize context instance """
        super().__init__()
        self.context = context

    def load(self, config_variable, config_file, suite):
        """ Load and parse config """
        config = self._load_config(config_variable, config_file)
        if not self._validate_config_base(config, suite):
            raise ValueError("Invalid config")
        context_config = self._process_depots(config, suite)
        self.context.suite = suite
        self.context.config = context_config
        log.debug("Resulting context config: %s", self.context.config)
        log.info("Loaded %s suite configuration", self.context.suite)

    def _load_config(self, config_variable, config_file):
        config_data = os.environ.get(config_variable, None)
        if not config_data:
            log.info("Loading config from %s", config_file)
            with open(config_file, "rb") as file_:
                config_data = file_.read()
        else:
            log.info("Loading config from %s", config_variable)
        config = self._variable_substitution(
            yaml.load(
                os.path.expandvars(config_data),
                Loader=yaml.FullLoader
            )
        )
        return config

    def _variable_substitution(self, obj):
        """ Allows to use raw environmental variables inside YAML/JSON config """
        if isinstance(obj, dict):
            for key in list(obj.keys()):
                obj[self._variable_substitution(key)] = \
                    self._variable_substitution(obj.pop(key))
        if isinstance(obj, list):
            for index, item in enumerate(obj):
                obj[index] = self._variable_substitution(item)
        if isinstance(obj, str):
            if re.match(r"^\$\![a-zA-Z_][a-zA-Z0-9_]*$", obj.strip()) \
                    and obj.strip()[2:] in os.environ:
                return os.environ[obj.strip()[2:]]
        return obj

    def _process_depots(self, config, suite):  # pylint: disable=R0912
        """ Process depots: resolve Vault variables and merge config from MinIO """
        context_config = recursive_merge(config["global"], config["suites"].get(suite))
        # Make HashiCorp Vault client
        vault_client = None
        if context_config["settings"].get("depots", dict()).get("vault", None):
            vault_config = context_config["settings"]["depots"]["vault"]
            vault_client = self._create_vault_client(vault_config)
        # Get vault secrets
        vault_secrets = None
        if vault_client:
            try:
                vault_secrets = vault_client.secrets.kv.v2.read_secret_version(
                    path=vault_config.get("secrets_path", "carrier-secrets"),
                    mount_point=vault_config.get("secrets_mount_point", "carrier-kv")
                ).get("data", dict()).get("data", dict())
            except:
                log.exception("Failed to get Vault secrets")
        # Resolve vault secrets in config
        if vault_secrets:
            context_config = self._vault_substitution(context_config, vault_secrets)
            log.info("Resolved secrets from Vault")
        # Make MinIO client
        minio_client = None
        if context_config["settings"].get("depots", dict()).get("minio", None):
            minio_config = context_config["settings"]["depots"]["minio"]
            minio_client = self._create_minio_client(minio_config)
        # Read base config
        base_config = self._minio_read_config_object(
            minio_client,
            minio_config.get("bucket", "carrier"),
            "__base__.yaml",
            vault_secrets
        )
        # Read project config
        project_config = dict()
        if minio_config.get("object", None):
            project_config = self._minio_read_config_object(
                minio_client,
                minio_config.get("bucket", "carrier"),
                minio_config.get("object", "config.yaml"),
                vault_secrets
            )
        # Read override config
        override_config = self._minio_read_config_object(
            minio_client,
            minio_config.get("bucket", "carrier"),
            "__override__.yaml",
            vault_secrets
        )
        # Merge resulting config
        return recursive_merge(
            recursive_merge(
                recursive_merge(base_config, context_config), project_config
            ), override_config
        )

    def _create_minio_client(self, minio_config):
        try:
            for key in ["endpoint"]:
                if key not in minio_config:
                    log.error("No MinIO %s in config")
                    return None
            http_client = None
            if not minio_config.get("ssl_verify", False):
                http_client = urllib3.PoolManager(
                    timeout=urllib3.Timeout.DEFAULT_TIMEOUT,
                    cert_reqs="CERT_NONE",
                    maxsize=10,
                    retries=urllib3.Retry(
                        total=5,
                        backoff_factor=0.2,
                        status_forcelist=[500, 502, 503, 504]
                    )
                )
            client = minio.Minio(
                endpoint=minio_config["endpoint"],
                access_key=minio_config.get("access_key", None),
                secret_key=minio_config.get("secret_key", None),
                secure=minio_config.get("secure", True),
                region=minio_config.get("region", None),
                http_client=http_client
            )
            # Test client auth
            client.list_buckets()
            return client
        except:
            log.exception("Error during MinIO client creation")
            return None

    def _minio_read_config_object(self, minio_client, bucket, object_, vault_secrets=None):
        result = dict()
        if minio_client:
            try:
                data = minio_client.get_object(bucket, object_)
                result = self._variable_substitution(
                    yaml.load(
                        os.path.expandvars(data.read()),
                        Loader=yaml.FullLoader
                    )
                )
                if vault_secrets:
                    result = self._vault_substitution(result, vault_secrets)
            except:
                pass
        return result

    def _create_vault_client(self, vault_config):
        try:
            for key in ["url"]:
                if key not in vault_config:
                    log.error("No Vault %s in config")
                    return None
            client = hvac.Client(
                url=vault_config["url"],
                verify=vault_config.get("ssl_verify", False)
            )
            if "auth_token" in vault_config:
                client.token = vault_config["auth_token"]
            if "auth_username" in vault_config:
                client.auth_userpass(
                    vault_config.get("auth_username"), vault_config.get("auth_password", "")
                )
            if "auth_role_id" in vault_config:
                client.auth_approle(
                    vault_config.get("auth_role_id"), vault_config.get("auth_secret_id", "")
                )
            if not client.is_authenticated():
                log.error("Vault authentication failed")
                return None
            return client
        except:
            log.exception("Error during Vault client creation")
            return None

    def _vault_substitution(self, obj, vault_secrets):
        """ Allows to use vault secrets inside YAML/JSON config """
        if isinstance(obj, dict):
            for key in list(obj.keys()):
                obj[self._vault_substitution(key, vault_secrets)] = \
                    self._vault_substitution(obj.pop(key), vault_secrets)
        if isinstance(obj, list):
            for index, item in enumerate(obj):
                obj[index] = self._vault_substitution(item, vault_secrets)
        if isinstance(obj, str):
            if re.match(r"^\$\=\S*$", obj.strip()) \
                    and obj.strip()[2:] in vault_secrets:
                return vault_secrets[obj.strip()[2:]]
        return obj

    def _validate_config_base(self, config, suite):
        if config.get(constants.CONFIG_VERSION_KEY, 0) != constants.CURRENT_CONFIG_VERSION:
            log.error("Invalid config version")
            return False
        if "global" not in config:
            config["global"] = dict()
        if "suites" not in config:
            log.error("Suites are not defined")
            return False
        if not config["suites"].get(suite, None):
            log.error("Suite is not defined: %s", suite)
            log.info("Available suites: %s", ", ".join(list(config["suites"])))
            return False
        if "settings" not in config["suites"][suite]:
            config["suites"][suite]["settings"] = dict()
        return True

    def list_suites(self, config_variable, config_file):
        """ List available suites from config """
        config = self._load_config(config_variable, config_file)
        if "suites" not in config:
            log.error("Suites are not defined")
            return list()
        return list(config["suites"])

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(
            len(data_obj), constants.CONFIG_VERSION_KEY, constants.CURRENT_CONFIG_VERSION
        )
        data_obj.insert(
            len(data_obj), "global", CommentedMap(), comment="Common settings for all suites"
        )
        data_obj.insert(len(data_obj), "suites", CommentedMap(), comment="Test suites")
        global_obj = data_obj["global"]
        global_obj.insert(
            len(global_obj), "settings", CommentedMap(), comment="General config"
        )
        settings_obj = global_obj["settings"]
        settings_obj.insert(
            len(settings_obj), "depots", CommentedMap(), comment="Upstream setting providers config"
        )
        depots_obj = settings_obj["depots"]
        depots_obj.insert(
            len(depots_obj), "vault", CommentedMap(), comment="HashiCorp Vault depot"
        )
        depots_obj.insert(
            len(depots_obj), "minio", CommentedMap(), comment="MinIO depot"
        )
        vault_obj = depots_obj["vault"]
        vault_obj.insert(
            len(vault_obj), "url", "https://vault.example.com:8200", comment="Vault URL"
        )
        vault_obj.insert(
            len(vault_obj), "secrets_path", "carrier-kv",
            comment="Secrets path"
        )
        vault_obj.insert(
            len(vault_obj), "secrets_mount_point", "secret",
            comment="(optional) Secrets KV V2 mount point"
        )
        vault_obj.insert(
            len(vault_obj), "ssl_verify", True,
            comment="(optional) Verify SSL certificate: True, False or path to CA bundle"
        )
        vault_obj.insert(
            len(vault_obj), "auth_token", "VAULT_TOKEN_VALUE",
            comment="(optional) Auth via token"
        )
        vault_obj.insert(
            len(vault_obj), "auth_username", "vault_username_value",
            comment="(optional) Auth via username/password"
        )
        vault_obj.insert(
            len(vault_obj), "auth_password", "vault_password_value",
            comment="(optional) Auth via username/password"
        )
        vault_obj.insert(
            len(vault_obj), "auth_role_id", "vault_approle_id_value",
            comment="(optional) Auth via approle id/secret id"
        )
        vault_obj.insert(
            len(vault_obj), "auth_secret_id", "vault_approle_secret_id_value",
            comment="(optional) Auth via approle id/secret id"
        )
        minio_obj = depots_obj["minio"]
        minio_obj.insert(
            len(minio_obj), "endpoint", "minio.example.com:9000",
            comment="S3 object storage endpoint"
        )
        minio_obj.insert(
            len(minio_obj), "bucket", "carrier",
            comment="Carrier bucket name"
        )
        minio_obj.insert(
            len(minio_obj), "object", "MY-PROJECT_Application.yaml",
            comment="Config file (object) name. Optional if only base and override are used"
        )
        minio_obj.insert(
            len(minio_obj), "access_key", "ACCESSKEYVALUE",
            comment="(optional) Access key for the object storage endpoint"
        )
        minio_obj.insert(
            len(minio_obj), "secret_key", "SECRETACCESSKEYVALUE",
            comment="(optional) Secret key for the object storage endpoint."
        )
        minio_obj.insert(
            len(minio_obj), "secure", True,
            comment="(optional) Set this value to True to enable secure (HTTPS) access"
        )
        minio_obj.insert(
            len(minio_obj), "ssl_verify", True,
            comment="(optional) Verify SSL certificate: True or False"
        )
        minio_obj.insert(
            len(minio_obj), "region", "us-east-1",
            comment="(optional) Set this value to override automatic bucket location discovery"
        )
