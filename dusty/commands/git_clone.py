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

import os
import getpass

import dulwich  # pylint: disable=E0401
from dulwich import porcelain  # pylint: disable=E0401
from dulwich.contrib.paramiko_vendor import ParamikoSSHVendor  # pylint: disable=E0401

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
        argparser.add_argument(
            "-b", "--branch", dest="branch",
            help="repository branch",
            type=str, default="master"
        )
        argparser.add_argument(
            "-l", "--lightweight", dest="depth",
            help="limit clone depth",
            type=int
        )
        argparser.add_argument(
            "-u", "--username", dest="username",
            help="username",
            type=str
        )
        argparser.add_argument(
            "-p", "--password", dest="password",
            help="password",
            type=str
        )
        argparser.add_argument(
            "-k", "--key", dest="key",
            help="SSH key file",
            type=str
        )


    def execute(self, args):
        """ Run the command """
        log.debug("Starting")
        # Check args
        if not args.source or not args.target:
            log.error("Please specify source and target.")
            return
        # Patch dulwich to work without valid UID/GID
        dulwich.repo.__original__get_default_identity = dulwich.repo._get_default_identity  # pylint: disable=W0212
        dulwich.repo._get_default_identity = _dulwich_repo_get_default_identity  # pylint: disable=W0212
        # Patch dulwich to use paramiko SSH client
        dulwich.client.get_ssh_vendor = ParamikoSSHVendor
        # Set USERNAME if needed
        try:
            getpass.getuser()
        except:  # pylint: disable=W0702
            os.environ["USERNAME"] = "git"
        # Clone repository
        depth = None
        if args.depth:
            depth = args.depth
        auth_args = dict()
        if args.username:
            auth_args["username"] = args.username
        if args.password:
            auth_args["password"] = args.password
        if args.key:
            auth_args["key_filename"] = args.key
        repository = porcelain.clone(
            args.source, args.target,
            checkout=False, depth=depth,
            **auth_args
        )
        # Checkout branch
        repository.reset_index(
            repository[b"refs/remotes/origin/" + args.branch.encode("utf-8")].tree
        )

    @staticmethod
    def get_name():
        """ Command name """
        return "git-clone"

    @staticmethod
    def get_description():
        """ Command help message (description) """
        return "clone remote git repository"


def _dulwich_repo_get_default_identity():
    try:
        return dulwich.repo.__original__get_default_identity()  # pylint: disable=W0212
    except:  # pylint: disable=W0702
        return ("Carrier User", "dusty@localhost")
