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
    Command: git-clone
"""

import dulwich  # pylint: disable=E0401

from dusty.tools import log
from dusty.models.module import ModuleModel
from dusty.models.command import CommandModel


class Command(ModuleModel, CommandModel):
    """ Generate sample config """

    def __init__(self, argparser):
        """ Initialize command instance, add arguments """
        super().__init__()
        argparser.add_argument(
            "-r", "--repository", dest="source",
            help="source git repository",
            type=str
        )
        argparser.add_argument(
            "-t", "--target", dest="target",
            help="target directory",
            type=str
        )

    def execute(self, args):
        """ Run the command """
        log.debug("Starting")
        #
        if not args.source or not args.target:
            log.error("Please specify source and target.")
            return
        #
        dulwich.porcelain.clone(args.source, args.target)

    @staticmethod
    def get_name():
        """ Command name """
        return "git-clone"

    @staticmethod
    def get_description():
        """ Command help message (description) """
        return "clone remote git repository"
