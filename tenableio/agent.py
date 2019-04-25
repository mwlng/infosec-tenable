# -*- coding: utf-8 -*-

"""
Tenable agent class 
"""

from tenable.io import TenableIO

class TenableAgent(object):
    def __init__(self, access_key, secret_key):
        self._access_key = access_key
        self._secret_key = secret_key

    def __enter__(self):
        self._io = TenableIO(self._access_key, 
                             self._secret_key)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def get_agents(self):
        return self._io.agents.list()

    def get_agent_details(self):
        return self._io.agents.details()

    def unlink_agents(self, agents):
        return self._io.agents.unlink(*agents)
