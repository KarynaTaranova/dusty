#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011,R0903,R0201

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

    def _process_depots(self, config, suite):
        """ Process depots: resolve Vault variables and merge config from MinIO """
        context_config = recursive_merge(config["global"], config["suites"].get(suite))
        # HashiCorp Vault
        if context_config["settings"].get("depots", dict()).get("vault", None):
            vault_config = context_config["settings"]["depots"]["vault"]
            log.debug("Vault config: %s", vault_config)
        # MinIO
        if context_config["settings"].get("depots", dict()).get("minio", None):
            minio_config = context_config["settings"]["depots"]["minio"]
            log.debug("MinIO config: %s", minio_config)
        return context_config

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
