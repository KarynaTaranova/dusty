#!/usr/bin/python3
# coding=utf-8
# pylint: skip-file

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
    Code from Dusty 1.0
"""

import json

from . import constants


__author__ = 'KarynaTaranova'


class GitleaksScanParser(object):
    def __init__(self, data):
        dupes = dict()
        self.items = []

        data = json.load(open(data))

        for item in data:
            title = self.get_title(item)
            if title in dupes:
                dupes[title]["commits"].add(item.get("commit"))
            else:
                dupes[title] = {
                    "description": item.get('info'),
                    "severity": item.get('severity'),
                    "date": item.get('date'),
                    "rule": item.get('rule'),
                    "file_path": item.get('file'),
                    "commits": {item.get("commit")}
                }

        for key, item in dupes.items():
            commits_str = ',\n\n'.join(item.get('commits'))
            self.items.append({
                "title": key,
                "description": f"{item.get('description')}.\n\nCommits:\n\n{commits_str}",
                "severity": constants.RULES_SEVERITIES.get(item.get('rule'), 'Medium'),
                "file_path": item.get('file_path'),
                "date": item.get('date')
            })

    def get_title(self, item):
        return f"{item.get('rule')} in {item.get('file')} file detected"
