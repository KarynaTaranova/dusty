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
    Processor: issue_hash
"""

import re
import hashlib

from dusty.tools import log
from dusty.models.module import DependentModuleModel
from dusty.models.processor import ProcessorModel
from dusty.models.finding import DastFinding


class Processor(DependentModuleModel, ProcessorModel):
    """ Process findings: inject issue_hash for compatibility during 1.0->2.0 migration """

    def __init__(self, context):
        """ Initialize processor instance """
        super().__init__()
        self.context = context
        self.config = \
            self.context.config["processing"][__name__.split(".")[-2]]

    def execute(self):
        """ Run the processor """
        log.info("Injecting issue hashes")
        for item in self.context.findings:
            issue_hash = None
            # Legacy code: prepare issue hash
            # Original:
            # def finding_error_string(self) -> str:
            #     endpoint_str = ""
            #     for e in self.endpoints:
            #         endpoint_str += str(e)
            #     return f'{self.finding["title"]}_' \
            #            f'{self.finding["static_finding_details"]["cwe"]}_' \
            #            f'{self.finding["static_finding_details"]["line_number"]}_' \
            #            f'{self.finding["static_finding_details"]["file_name"]}_' \
            #            f'{endpoint_str}'
            # def get_hash_code(self) -> str:
            #     hash_string = self.finding_error_string().strip()
            #     logging.info("Finding error string: '%s'", hash_string)
            #     return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
            if isinstance(item, DastFinding):
                title = re.sub('[^A-Za-zА-Яа-я0-9//\\\.\- _]+', '', item.title)  # pylint: disable=W1401
                issue_hash = hashlib.sha256(
                    f'{title}_None_None__'.strip().encode('utf-8')
                ).hexdigest()
            # Inject issue hash
            if issue_hash:
                item.set_meta("issue_hash", issue_hash)
                item.description += f"\n\n**Issue Hash:** {issue_hash}"

    @staticmethod
    def get_name():
        """ Module name """
        return "Issue hash injector"

    @staticmethod
    def get_description():
        """ Module description """
        return "Injects issue hashes into findings"