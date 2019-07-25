#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011,W1401,E0401,R0914,R0915,R0912

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
    PT AI HTML parser
"""

# import base64
# import hashlib

# from urllib.parse import urlparse
# from lxml import etree

# from dusty.tools import log, url, markdown
# from dusty.models.finding import DastFinding

from dusty.tools import log

from .legacy import PTAIScanParser
from . import constants


def parse_findings(output_file, scanner):  # pylint: disable=E,W,R,C
    """ Parse findings (code from dusty 1.0) """
    filtered_statuses = scanner.config.get(
        "filtered_statuses", constants.PTAI_DEFAULT_FILTERED_STATUSES
    )
    findings = PTAIScanParser(output_file, filtered_statuses).items
    log.debug("Findings: %s", findings)
