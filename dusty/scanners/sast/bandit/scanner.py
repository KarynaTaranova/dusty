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
    Scanner: bandit
"""

from dusty.tools import log
from dusty.models.module import DependentModuleModel
from dusty.models.scanner import ScannerModel


class Scanner(DependentModuleModel, ScannerModel):
    """ Scanner class """

    def __init__(self, context):
        """ Initialize scanner instance """
        self.context = context
        self.config = \
            self.context.config["scanners"][__name__.split(".")[-3]][__name__.split(".")[-2]]
        self.results = list()
        self.errors = list()
        self.meta = dict()

    def execute(self):
        """ Run the scanner """
        log.debug(f"Config: {self.config}")

    def get_results(self):
        """ Get results """
        return self.results

    def get_errors(self):
        """ Get errors """
        return self.errors

    def get_meta(self, name, default=None):
        """ Get meta value """
        if name in self.meta:
            return self.meta[name]
        return default

    def set_meta(self, name, value):
        """ Set meta value """
        self.meta[name] = value

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(len(data_obj), "code", "/path/to/code", comment="scan target")

    @staticmethod
    def validate_config(config):
        """ Validate config """
        log.debug(f"Config: {config}")

    @staticmethod
    def depends_on():
        """ Return required depencies """
        return []

    @staticmethod
    def run_after():
        """ Return optional depencies """
        return []

    @staticmethod
    def get_name():
        """ Module name """
        return "bandit"

    @staticmethod
    def get_description():
        """ Module description or help message """
        return "SAST scanner"