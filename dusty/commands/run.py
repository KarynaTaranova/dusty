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

from dusty.tools import log
from dusty import constants
from dusty.models.module import ModuleModel
from dusty.models.command import CommandModel
from dusty.helpers.context import RunContext
from dusty.helpers.config import ConfigHelper
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
        config = ConfigHelper(context)
        if args.list_suites:
            suites = config.list_suites(args.config_variable, args.config_file)
            log.info("Available suites: %s", ", ".join(suites))
            return
        if not args.suite:
            log.error("Suite is not defined. Use --help to get help")
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
    def get_name():
        """ Command name """
        return "run"

    @staticmethod
    def get_description():
        """ Command help message (description) """
        return "run tests according to config"
