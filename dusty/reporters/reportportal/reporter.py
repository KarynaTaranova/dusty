#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011,E0401

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
    Reporter: reportportal
"""

from dusty.tools import log
from dusty.models.module import DependentModuleModel
from dusty.models.reporter import ReporterModel

# from .legacy import RedisFile


class Reporter(DependentModuleModel, ReporterModel):
    """ Report findings from scanners """

    def __init__(self, context):
        """ Initialize reporter instance """
        super().__init__()
        self.context = context
        self.config = \
            self.context.config["reporters"][__name__.split(".")[-2]]
        # Prepare config object (code from legacy 'parse_rp_config')
        self._rp_config = {
            "rp_project": self.config.get("rp_project_name", "Dusty"),
            "rp_launch_name": self.config.get("rp_launch_name", self.context.suite),
            "rp_url": self.config.get("rp_host"),
            "rp_token": self.config.get("rp_token"),
        }
        self._rp_config["rp_launch_tags"] = self.config.get("rp_launch_tags", None)

    # def report(self):
    #     """ Report """
    #     log.info("Reporting to ReportPortal")

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(
            len(data_obj),
            "rp_host", "https://rp.com",
            comment="url to ReportPortal.io deployment"
        )
        data_obj.insert(
            len(data_obj),
            "rp_token", "XXXXXXXXXXXXX",
            comment="ReportPortal authentication token"
        )
        data_obj.insert(
            len(data_obj),
            "rp_project_name", "XXXXXX",
            comment="Name of a Project in ReportPortal to send results to"
        )
        data_obj.insert(
            len(data_obj),
            "rp_launch_name", "XXXXXXX",
            comment="Name of a Launch in ReportPortal to send results to"
        )

    @staticmethod
    def validate_config(config):
        """ Validate config """
        required = ["rp_project_name", "rp_launch_name", "rp_host", "rp_token"]
        not_set = [item for item in required if item not in config]
        if not_set:
            error = f"Required configuration options not set: {', '.join(not_set)}"
            log.error(error)
            raise ValueError(error)

    @staticmethod
    def get_name():
        """ Reporter name """
        return "ReportPortal"

    @staticmethod
    def get_description():
        """ Reporter description """
        return "ReportPortal reporter"
