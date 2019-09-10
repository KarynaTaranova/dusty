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
import os

from dusty.tools import markdown


__author__ = 'KarynaTaranova'


class GitleaksScanParser(object):
    def __init__(self, data):
        dupes = dict()
        find_date = None
        self.items = []

        data = json.load(open(data))

        for item in data:
            self.items.append({
                "title": f"{item.get('rule')} in {item.get('file')} file detected",
                "description": item.get('info'),
                "severity": item.get('severity', 'Medium'),
                "file_path": item.get('file')
            })
