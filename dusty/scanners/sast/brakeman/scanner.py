#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011,E0401,W0702,W0703

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
    Scanner: brakeman
"""

import os
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
        include_checks = list()
        if self.config.get("include_checks", None):
            include_checks.append("-t")
            include_checks.append(self.config.get("include_checks"))
        exclude_checks = list()
        if self.config.get("exclude_checks", None):
            exclude_checks.append("-x")
            exclude_checks.append(self.config.get("exclude_checks"))
        excluded_files = list()
        if self.config.get("excluded_files", None):
            excluded_files.append("--skip-files")
            excluded_files.append(self.config.get("excluded_files"))
        task = subprocess.run(
            [
                "brakeman", "--no-exit-on-warn", "--no-exit-on-error", "-f", "json"
            ] + include_checks + exclude_checks + excluded_files + [self.config.get("code")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        log.log_subprocess_result(task)
        parse_findings(task.stdout.decode("utf-8", errors="ignore"), self)
        # Save intermediates
        self.save_intermediates(task.stdout)

    def save_intermediates(self, task_stdout):
        """ Save scanner intermediates """
        if self.config.get("save_intermediates_to", None):
            log.info("Saving intermediates")
            base = os.path.join(self.config.get("save_intermediates_to"), __name__.split(".")[-2])
            try:
                # Make directory for artifacts
                os.makedirs(base, mode=0o755, exist_ok=True)
                # Save report
                with open(os.path.join(base, "report.json"), "w") as report:
                    report.write(task_stdout.decode("utf-8", errors="ignore"))
            except:
                log.exception("Failed to save intermediates")

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(len(data_obj), "code", "/path/to/code", comment="scan target")

    @staticmethod
    def validate_config(config):
        """ Validate config """
        required = ["code"]
        not_set = [item for item in required if item not in config]
        if not_set:
            error = f"Required configuration options not set: {', '.join(not_set)}"
            log.error(error)
            raise ValueError(error)

    @staticmethod
    def get_name():
        """ Module name """
        return "brakeman"

    @staticmethod
    def get_description():
        """ Module description or help message """
        return "Ruby on Rails static analysis security vulnerability scanner"
