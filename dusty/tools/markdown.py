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


def markdown_to_html(text):
    """ Convert markdown to HTML """
    return markdown2.markdown(text, extras=["tables", "fenced-code-blocks", "wiki-tables"])


def markdown_escape(string):
    """ Escape markdown special symbols """
    to_escape = [
        "\\", "`", "*", "_",
        "{", "}", "[", "]", "(", ")",
        "#", "|", "+", "-", ".", "!"
    ]
    for item in to_escape:
        string = string.replace(item, f"\\{item}")
    return string


def markdown_unescape(string):
    """ Un-escape markdown special symbols """
    to_escape = [
        "\\", "`", "*", "_",
        "{", "}", "[", "]", "(", ")",
        "#", "|", "+", "-", ".", "!"
    ]
    for item in to_escape:
        string = string.replace(f"\\{item}", item)
    return string


def markdown_table_escape(string):
    """ Escape markdown special symbols in tables """
    return markdown_escape(string).replace("\n", " ")


def html_to_text(html, escape=True):
    """ Convert HTML to markdown """
    text = inscriptis.get_text(html, display_links=True)
    if escape:
        text = markdown_escape(text)
    return text
