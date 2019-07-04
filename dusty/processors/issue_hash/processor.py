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
            # Legacy code: prepare issue hash
            title = re.sub('[^A-Za-zА-Яа-я0-9//\\\.\- _]+', '', item.title)
            issue_hash = hashlib.sha256(
                f'{title}_None_None_None_'.strip().encode('utf-8')
            ).hexdigest()
            # Inject issue hash
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
