#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011,E0401,R0903

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
    Qualys API helper
"""

import time
import requests

from dusty.tools import log
# from dusty.models.error import Error


class QualysHelper:
    """ Helps to query Qualys API """

    def __init__(self, context, server, login, password, retries=5, retry_delay=2.5):  # pylint: disable=R0913
        self.context = context
        self.server = server
        self.login = login
        self.password = password
        self.retries = retries
        self.retry_delay = retry_delay
        self._connection_obj = None

    @property
    def _connection(self):
        """ Prepare connection object """
        if self._connection_obj is None:
            self._connection_obj = requests.Session()
            self._connection_obj.auth = (self.login, self.password)
            self._connection_obj.headers.update({"Accept": "application/json"})
        return self._connection_obj

    def _destroy_connection(self):
        """ Destroy connection object """
        if self._connection_obj is not None:
            self._connection_obj.close()
            self._connection_obj = None

    def _request(self, endpoint, json=None, validator=None):
        """ Perform API request (with error handling) """
        for retry in range(self.retries):
            try:
                response = self._request_raw(endpoint, json)
                if validator is not None and not validator(response):
                    raise ValueError("Invalid response")
                return response
            except:  # pylint: disable=W0702
                log.exception("Qualys API error [retry=%d]", retry)
                self._destroy_connection()
                time.sleep(self.retry_delay)
        raise RuntimeError(f"Qualys API request failed after {self.retries} retries")

    def _request_raw(self, endpoint, json=None):
        """ Perform API request (directly) """
        api = self._connection
        if json is None:
            response = api.get(f"{self.server}{endpoint}")
        else:
            response = api.post(f"{self.server}{endpoint}", json=json)
        log.debug(
            "API response: %d [%s] %s",
            response.status_code, response.headers, response.text
        )
        return response

    def search_for_project(self, project_name):
        """ Search for existing project and get ID """
        response = self._request(
            "/qps/rest/3.0/search/was/webapp",
            json={
                "ServiceRequest": {
                    "filters": [{
                        "Criteria": {
                            "field": "name",
                            "operator": "EQUALS",
                            "data": project_name
                        }
                    }]
                }
            },
            validator=lambda r: r.ok
        )
        return response
