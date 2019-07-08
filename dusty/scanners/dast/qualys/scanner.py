#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011,E0401,W0702,W0703,R0902

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
    Scanner: Qualys WAS
"""

from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.comments import CommentedMap

from dusty.tools import log
from dusty.models.module import DependentModuleModel
from dusty.models.scanner import ScannerModel


class Scanner(DependentModuleModel, ScannerModel):
    """ Scanner class """

    def __init__(self, context):
        """ Initialize scanner instance """
        super().__init__()
        self.context = context
        self.config = \
            self.context.config["scanners"][__name__.split(".")[-3]][__name__.split(".")[-2]]

    def execute(self):
        """ Run the scanner """

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(
            len(data_obj), "qualys_api_server", "https://qualysapi.qualys.eu",
            comment="Qualys API server URL"
        )
        data_obj.insert(
            len(data_obj), "qualys_login", "some-user",
            comment="Qualys user login"
        )
        data_obj.insert(
            len(data_obj), "qualys_password", "S0m3P@ssw0rd",
            comment="Qualys user password"
        )
        data_obj.insert(
            len(data_obj), "qualys_option_profile_id", 12345,
            comment="Qualys option profile ID"
        )
        data_obj.insert(
            len(data_obj), "qualys_report_template_id", 12345,
            comment="Qualys report template ID"
        )
        data_obj.insert(
            len(data_obj), "qualys_scanner_type", "EXTERNAL",
            comment="Qualys scanner type: EXTERNAL or INTERNAL"
        )
        data_obj.insert(
            len(data_obj), "qualys_scanner_pool", CommentedSeq(),
            comment="(INTERNAL only) Qualys scanner pool: list of scanner appliances to choose from"
        )
        pool_obj = data_obj["qualys_scanner_pool"]
        pool_obj.append("MY_SCANNER_Name1")
        pool_obj.append("MY_SCANNER_Name2")
        pool_obj.append("MY_OTHERSCANNER_Name")
        data_obj.insert(len(data_obj), "random_name", False, comment="Use random project name")
        data_obj.insert(len(data_obj), "target", "http://app:8080", comment="scan target")
        data_obj.insert(
            len(data_obj), "exclude", ["http://app:8080/logout.*"],
            comment="(optional) URLs regex to exclude from scan"
        )
        data_obj.insert(
            len(data_obj), "auth_login", "user",
            comment="(optional) User login for authenticated scan"
        )
        data_obj.insert(
            len(data_obj), "auth_password", "P@ssw0rd",
            comment="(optional) User password for authenticated scan"
        )
        data_obj.insert(
            len(data_obj), "auth_script", CommentedSeq(),
            comment="(optional) Selenium-like script for authenticated scan"
        )
        script_obj = data_obj["auth_script"]
        for command in [
                {"command": "open", "target": "%Target%/login", "value": ""},
                {"command": "waitForElementPresent", "target": "id=login_login", "value": ""},
                {"command": "waitForElementPresent", "target": "id=login_password", "value": ""},
                {"command": "waitForElementPresent", "target": "id=login_0", "value": ""},
                {"command": "type", "target": "id=login_login", "value": "%Username%"},
                {"command": "type", "target": "id=login_password", "value": "%Password%"},
                {"command": "clickAndWait", "target": "id=login_0", "value": ""}
        ]:
            command_obj = CommentedMap()
            command_obj.fa.set_flow_style()
            for key in ["command", "target", "value"]:
                command_obj.insert(len(command_obj), key, command[key])
            script_obj.append(command_obj)

    @staticmethod
    def validate_config(config):
        """ Validate config """
        required = ["target"]
        not_set = [item for item in required if item not in config]
        if not_set:
            error = f"Required configuration options not set: {', '.join(not_set)}"
            log.error(error)
            raise ValueError(error)

    @staticmethod
    def get_name():
        """ Module name """
        return "Qualys WAS"

    @staticmethod
    def get_description():
        """ Module description or help message """
        return "Qualys (R) Web Application Scanning"
