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
    Scanner: AEM Hacker
"""

import subprocess

from dusty.tools import log
from dusty.models.module import DependentModuleModel
from dusty.models.scanner import ScannerModel

from .parser import parse_findings


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
        task = subprocess.run([
            "aem-wrapper.sh", "-u", self.config.get("target"),
            "--host", self.config.get("scanner_host", "127.0.0.1"),
            "--port", self.config.get("scanner_port", "4444")
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log.debug("Tast result: %s", task)
        parse_findings(task.stdout, self)

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(len(data_obj), "target", "http://app:4502", comment="scan target")
        data_obj.insert(
            len(data_obj), "scanner_host", "127.0.0.1",
            comment="(optional) IP of scanner instance (for SSRF detection)"
        )
        data_obj.insert(
            len(data_obj), "scanner_port", "4444",
            comment="(optional) published scanner port to use during SSRF detection"
        )

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
        return "AEM Hacker"

    @staticmethod
    def get_description():
        """ Module description or help message """
        return "AEM Hacker scanner"
