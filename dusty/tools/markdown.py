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
    Markdown tools
"""

import markdown2
import inscriptis

from dusty.tools import log


def markdown_to_html(text):
    """ Convert markdown to HTML """
    return markdown2.markdown(text, extras=["tables", "fenced-code-blocks"])


def markdown_table_escape(string):
    """ Escape markdown special symbols in tables """
    to_escape = [
        "\\", "`", "*", "_",
        "{", "}", "[", "]", "(", ")",
        "#", "|", "+", "-", ".", "!"
    ]
    for item in to_escape:
        string = string.replace(item, f"\\{item}")
    return string.replace("\n", " ")


def markdown_escape(string):
    """ Escape markdown special symbols """
    to_escape = [
        "\\", "`", "*", "_",
        "{", "}", "[", "]", "(", ")",
        "#", "|", "+", "-", ".", "!"
    ]
    for item in to_escape:
        string = string.replace(item, f"\\{item}")
    return string.replace("\n", " ")


def html_to_text(html, escape=True):
    """ Convert HTML to markdown """
    text = inscriptis.get_text(html)
    log.debug(f"HTML: {text}")
    if escape:
        text = markdown_escape(text)
        log.debug(f"Escaped: {text}")
    return text
