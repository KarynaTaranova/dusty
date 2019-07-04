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
    Constants
"""


# Legacy
JIRA_FIELD_DO_NOT_USE_VALUE = '!remove'
JIRA_FIELD_USE_DEFAULT_VALUE = '!default'
JIRA_SEVERITIES = {
    'Trivial': 4,
    'Minor': 3,
    'Medium': 2,
    'Major': 1,
    'Critical': 0,
    'Blocker': 0
}
JIRA_ALTERNATIVES = {
    'Trivial': ['Low', 'Minor'],
    'Minor': ['Low', 'Medium'],
    'Medium': ['Major'],
    'Major': ['High', 'Critical'],
    'Critical': ['Very High', 'Blocker'],
    'Blocker': ['Very High', 'Critical']
}
JIRA_OPENED_STATUSES = ['Open', 'In Progress']

# Priority/Severity mapping
JIRA_SEVERITY_MAPPING = {
    "Critical": "Critical",
    "High": "Major",
    "Medium": "Medium",
    "Low": "Minor",
    "Info": "Trivial"
}