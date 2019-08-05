#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011

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
    Depot tools
"""

from dusty.models.depot import SecretDepotModel, ObjectDepotModel


def get_secret(context, key):
    """ Get secret by key from enabled depots """
    for depot in context.depots.values():
        if isinstance(depot, SecretDepotModel):
            try:
                value = depot.get_secret(key)
                if value is not None:
                    return value
            except:  # pylint: disable=W0702
                pass
    return None


def get_object(context, key):
    """ Get object by key from enabled depots """
    for depot in context.depots.values():
        if isinstance(depot, ObjectDepotModel):
            try:
                value = depot.get_object(key)
                if value is not None:
                    return value
            except:  # pylint: disable=W0702
                pass
    return None


def put_object(context, key, data):
    """ Put object by key into enabled depots """
    for depot in context.depots.values():
        if isinstance(depot, ObjectDepotModel):
            try:
                result = depot.put_object(key, data)
                if result:
                    return
            except:  # pylint: disable=W0702
                pass
