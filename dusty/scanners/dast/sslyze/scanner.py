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
    Scanner: SSLyze
"""

import os
import shutil
import tempfile
import subprocess

from dusty.tools import log, url
from dusty.models.module import DependentModuleModel
from dusty.models.scanner import ScannerModel

# from .parser import parse_findings


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
        # Get target host IP
        target_url = url.parse_url(self.config.get("target"))
        # Make temporary files
        output_file_fd, output_file = tempfile.mkstemp()
        log.debug("Output file: %s", output_file)
        os.close(output_file_fd)
        # Scan target
        task = subprocess.run([
            "sslyze", "--regular", f"--json_out={output_file}", "--quiet",
            f"{target_url.hostname}:{url.get_port(target_url)}"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Parse findings
        # parse_findings(output_file, self)
        # Save intermediates
        self.save_intermediates(output_file, task)
        # Remove temporary files
        os.remove(output_file)

    def save_intermediates(self, output_file, task):
        """ Save scanner intermediates """
        if self.config.get("save_intermediates_to", None):
            log.info("Saving intermediates")
            base = os.path.join(self.config.get("save_intermediates_to"), __name__.split(".")[-2])
            try:
                # Make directory for artifacts
                os.makedirs(base, mode=0o755, exist_ok=True)
                # Save report
                shutil.copyfile(
                    output_file,
                    os.path.join(base, "report.json")
                )
                # Save output
                with open(os.path.join(base, "output.stdout"), "w") as output:
                    output.write(task.stdout.decode("utf-8", errors="ignore"))
                with open(os.path.join(base, "output.stderr"), "w") as output:
                    output.write(task.stderr.decode("utf-8", errors="ignore"))
            except:
                log.exception("Failed to save intermediates")

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(len(data_obj), "target", "http://app:4502", comment="scan target")
        data_obj.insert(
            len(data_obj), "save_intermediates_to", "/data/intermediates/dast",
            comment="(optional) Save scan intermediates (raw results, logs, ...)"
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
        return "SSLyze"

    @staticmethod
    def get_description():
        """ Module description or help message """
        return "SSLyze SSL/TLS server scanner"
