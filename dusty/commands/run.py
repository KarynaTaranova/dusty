#!/usr/bin/python3
# coding=utf-8

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
    Command: run
"""

import pkg_resources

from dusty.tools import log
from dusty import constants
from dusty.models.module import ModuleModel
from dusty.models.command import CommandModel
from dusty.models.context import RunContext
from dusty.models.config import ConfigModel
from dusty.scanners.performer import ScanningPerformer
from dusty.processors.performer import ProcessingPerformer
from dusty.reporters.performer import ReportingPerformer


class Command(ModuleModel, CommandModel):
    """ Runs tests defined in config file """

    def __init__(self, argparser):
        """ Initialize command instance, add arguments """
        super().__init__()
        argparser.add_argument(
            "-e", "--config-variable", dest="config_variable",
            help="name of environment variable with config",
            type=str, default=constants.DEFAULT_CONFIG_ENV_KEY
        )
        argparser.add_argument(
            "-c", "--config-file", dest="config_file",
            help="path to config file",
            type=str, default=constants.DEFAULT_CONFIG_PATH
        )
        argparser.add_argument(
            "-s", "--suite", dest="suite",
            help="test suite to run",
            type=str
        )
        argparser.add_argument(
            "-l", "--list-suites", dest="list_suites",
            help="list available test suites",
            action="store_true"
        )

    def execute(self, args):
        """ Run the command """
        log.debug("Starting")
        if args.call_from_legacy:
            log.warning("Called from legacy entry point")
        # Init context
        context = RunContext(args)
        config = ConfigModel(context)
        if args.list_suites or not args.suite:
            suites = config.list_suites(args.config_variable, args.config_file)
            if not args.suite:
                log.error("Suite is not defined. Use --help to get help")
            log.info("Available suites: %s", ", ".join(suites))
            return
        # Make instances
        scanning = ScanningPerformer(context)
        processing = ProcessingPerformer(context)
        reporting = ReportingPerformer(context)
        # Add to context
        context.performers["scanning"] = scanning
        context.performers["processing"] = processing
        context.performers["reporting"] = reporting
        # Init config
        config.load(args.config_variable, args.config_file, args.suite)
        scanning.validate_config(context.config)
        processing.validate_config(context.config)
        reporting.validate_config(context.config)
        # Add meta to context
        self._fill_context_meta(context)
        # Prepare
        scanning.prepare()
        processing.prepare()
        reporting.prepare()
        # Perform
        scanning.perform()
        processing.perform()
        reporting.perform()
        # Done
        reporting.flush()
        log.debug("Done")

    @staticmethod
    def _fill_context_meta(context):
        # Project name
        if context.config["settings"].get("project_name", None):
            context.set_meta("project_name", context.config["settings"]["project_name"])
        # Project description
        if context.config["settings"].get("project_description", None):
            context.set_meta(
                "project_description", context.config["settings"]["project_description"]
            )
        # Environment name
        if context.config["settings"].get("environment_name", None):
            context.set_meta(
                "environment_name", context.config["settings"]["environment_name"]
            )
        # Testing type
        if context.config["settings"].get("testing_type", None):
            context.set_meta("testing_type", context.config["settings"]["testing_type"])
        # Scan type
        if context.config["settings"].get("scan_type", None):
            context.set_meta("scan_type", context.config["settings"]["scan_type"])
        # Build ID
        if context.config["settings"].get("build_id", None):
            context.set_meta("build_id", context.config["settings"]["build_id"])
        # Dusty version
        context.set_meta("dusty_version", pkg_resources.require("dusty")[0].version)
        # DAST target
        if context.config["settings"].get("dast", dict()).get("target", None):
            context.set_meta("dast_target", context.config["settings"]["dast"]["target"])
        # SAST code
        if context.config["settings"].get("sast", dict()).get("code", None):
            context.set_meta(
                "sast_code", context.config["settings"]["sast"]["code"]
            )

    @staticmethod
    def get_name():
        """ Command name """
        return "run"

    @staticmethod
    def get_description():
        """ Command help message (description) """
        return "run tests according to config"
