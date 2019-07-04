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
    Reporter: jira
"""

from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.comments import CommentedMap

from dusty.tools import log
from dusty.models.module import DependentModuleModel
from dusty.models.reporter import ReporterModel

# from . import constants
# from .legacy import JiraWrapper


class Reporter(DependentModuleModel, ReporterModel):
    """ Report findings from scanners """

    def __init__(self, context):
        """ Initialize reporter instance """
        super().__init__()
        self.context = context
        self.config = \
            self.context.config["reporters"][__name__.split(".")[-2]]

    def report(self):
        """ Report """
        log.info("Creating Jira tickets")

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(len(data_obj), "url", "https://jira.example.com", comment="Jira URL")
        data_obj.insert(
            len(data_obj), "username", "some_username", comment="Jira login"
        )
        data_obj.insert(
            len(data_obj), "password", "SomeSecurePassword", comment="Jira password"
        )
        data_obj.insert(
            len(data_obj), "project", "SOME-PROJECT", comment="Jira project"
        )
        data_obj.insert(
            len(data_obj), "fields", CommentedMap(), comment="Fields for created tickets"
        )
        fields_obj = data_obj["fields"]
        fields_obj.insert(
            len(fields_obj),
            "Issue Type", "Bug", comment="(field) Ticket type"
        )
        fields_obj.insert(
            len(fields_obj),
            "Assignee", "Ticket_Assignee", comment="(field) Assignee"
        )
        fields_obj.insert(
            len(fields_obj),
            "Epic Link", "SOMEPROJECT-1234", comment="(field) Epic"
        )
        fields_obj.insert(
            len(fields_obj),
            "Security Level", "SOME_LEVEL", comment="(field) Security level"
        )
        fields_obj.insert(
            len(fields_obj),
            "Components/s", CommentedSeq(), comment="(field) Component/s"
        )
        components_obj = fields_obj["Components/s"]
        component_obj = CommentedMap()
        component_obj.insert(len(component_obj), "name", "Component Name")
        components_obj.append(component_obj)

    @staticmethod
    def validate_config(config):
        """ Validate config """
        if "url" not in config:
            error = "No Jira server URL defined in config"
            log.error(error)
            raise ValueError(error)
        if "username" not in config:
            error = "No Jira login defined in config"
            log.error(error)
            raise ValueError(error)
        if "password" not in config:
            error = "No Jira password defined in config"
            log.error(error)
            raise ValueError(error)
        if "project" not in config:
            error = "No Jira project defined in config"
            log.error(error)
            raise ValueError(error)

    @staticmethod
    def get_name():
        """ Reporter name """
        return "Jira"

    @staticmethod
    def get_description():
        """ Reporter description """
        return "Jira reporter"
