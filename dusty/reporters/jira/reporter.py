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
from dusty.models.finding import DastFinding

from dusty.constants import SEVERITIES

# from . import constants
from .legacy import JiraWrapper


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
        # Prepare wrapper
        log.info("Creating legacy wrapper instance")
        wrapper = JiraWrapper(
            self.config.get("url"),
            self.config.get("username"),
            self.config.get("password"),
            self.config.get("project"),
            self.config.get("fields")
        )
        if not wrapper.valid:
            log.error("Jira configuration is invalid. Skipping Jira reporting")
            return
        log.debug("Legacy wrapper is valid")
        # Prepare findings
        findings = list()
        for item in self.context.findings:
            if item.get_meta("information_finding", False) or \
                    item.get_meta("false_positive_finding", False):
                continue
            if isinstance(item, DastFinding):
                findings.append({
                    "title": item.title,
                    "priority": "Minor",
                    "description": item.description,
                    "issue_hash": "deadbeef",
                    "additional_labels": [
                        item.get_meta("tool", ""),
                        "DAST", # self.scan_type
                        item.get_meta("severity", SEVERITIES[-1])
                    ],
                    "raw": item
                })
            else:
                raise ValueError("Unsupported item type")
        findings.sort(key=lambda item: (
            SEVERITIES.index(item["raw"].get_meta("severity", SEVERITIES[-1])),
            item["raw"].get_meta("tool", ""),
            item["raw"].title
        ))
        # Submit issues
        for finding in findings:
            issue, created = wrapper.create_issue(
                finding["title"], # title, self.finding["title"]
                finding["priority"], # priority
                finding["description"], # description,
                # self.__str__(overwrite_steps_to_reproduce=_overwrite_steps)
                finding["issue_hash"], # issue_hash, self.get_hash_code()
                # attachments=None,
                # get_or_create=True,
                finding["additional_labels"] # additional_labels=None
                # [self.finding["tool"], self.scan_type, self.finding["severity"]]
            )
            _ = issue, created

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
        data_obj.insert(
            len(data_obj), "custom_mapping", CommentedMap(), comment="Custom priority mapping"
        )
        mapping_obj = data_obj["custom_mapping"]
        mapping_obj.insert(
            len(mapping_obj),
            "Critical", "Very High"
        )
        mapping_obj.insert(
            len(mapping_obj),
            "Major", "High"
        )
        mapping_obj.insert(
            len(mapping_obj),
            "Medium", "Medium"
        )
        mapping_obj.insert(
            len(mapping_obj),
            "Minor", "Low"
        )
        mapping_obj.insert(
            len(mapping_obj),
            "Trivial", "Low"
        )

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
