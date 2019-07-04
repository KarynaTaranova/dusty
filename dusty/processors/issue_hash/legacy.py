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


class Endpoint(object):
    def __init__(self, protocol=None, host=None, fqdn=None, port=None, path=None, query=None, fragment=None, **kwargs):

        self.protocol = protocol  # The communication protocol such as 'http', 'ftp', etc.
        self.host = host    # The host name or IP address, you can also include the port number.
                            # For example '127.0.0.1', '127.0.0.1:8080', 'localhost', 'yourdomain.com'.
        self.fqdn = fqdn    # Fully qualified domain name (FQDN) is the complete domain name
        self.port = port    # The network port associated with the endpoint.
        self.path = path    # The location of the resource, it should start with a '/'.
                            # For example/endpoint/420/edit"
        self.query = query  # "The query string, the question mark should be omitted.
                            # For example 'group=4&team=8'"
        self.fragment = fragment  # "The fragment identifier which follows the hash mark. The hash mark should
                                  # be omitted. For example 'section-13', 'paragraph-2'."

    def __str__(self):
        str_repr = ""
        if self.protocol:
            str_repr = f'{self.protocol}://'
        if self.host:
            str_repr += self.fqdn if self.fqdn else self.host
        if self.port:
            str_repr += f":{self.port}"
        if self.path:
            str_repr += f"{self.path}"
        if self.query:
            str_repr += f"?{self.query}"
        return str_repr


def make_endpoint_from_url(url, include_query=True, include_fragment=True):
    """ Makes Enpoint instance from URL """
    parsed_url = url # parsed_url = parse_url(url)
    host_value = parsed_url.hostname
    protocol = parsed_url.protocol
    port = parsed_url.port
    if (protocol == "http" and port != "80") or (
            protocol == "https" and port != "443"):
        host_value = f'{parsed_url.hostname}:{parsed_url.port}'
    return Endpoint(
        protocol=parsed_url.protocol,
        host=host_value,
        fqdn=parsed_url.hostname,
        port=parsed_url.port,
        path=parsed_url.path,
        query=parsed_url.query if include_query else "",
        fragment=parsed_url.fragment if include_fragment else ""
    )
