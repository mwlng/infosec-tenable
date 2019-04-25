# -*- coding: utf-8 -*-

"""
Tenable client class 
"""

from tenable_io.client import TenableIOClient
from tenable_io.api.models import Scan
from tenable_io.exceptions import TenableIOApiException

class TenableClient(object):
    def __init__(self, access_key, secret_key):
        self._access_key = access_key
        self._secret_key = secret_key

    def __enter__(self):
        self._client = TenableIOClient(self._access_key, 
                                       self._secret_key)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def _get_scanner_list(self):
        return self._client.scanners_api.list()

    def get_scanners(self):
        try:
            scanner_list = self._get_scanner_list() 
            return scanner_list.scanners  
        except TenableIOApiException as ex:
            print(ex.message)

    def get_scanner_names(self):
        names = []
        scs = self.get_scanners()
        for sc in scs:
            names.append(sc.name) 
        return names

    def get_scanner_id(self, scanner_name):
        scs = self.get_scanners()
        for sc in scs:
            if sc.name == scanner_name:
                return sc.id
        return None

    def get_scanner_status(self, scanner_name):
        scs = self.get_scanners()
        for sc in scs:
            if scanner_name == sc.name:
                return sc.status
        return None 
        
    def get_aws_targets_by_name(self, scanner_name):
        targets = []
        scs = self.get_scanners()
        for sc in scs:
            if scanner_name == sc.name:
                aws_target_list = self._client.scanners_api.get_aws_targets(sc.id)
                targets = aws_target_list.targets
                break
        return targets

    def new_scan(self, scan_name, targets, template_name):
        return self._client.scan_helper.create(name=scan_name,
                                               text_targets=targets,
                                               template=template_name)

    def get_scan(self, scan_name):
        scans = self._client.scan_helper.scans(name=scan_name)
        if len(scans) and scans[0].name() == scan_name:
            return scans[0]
        else:
            return None

    def configure_scan(self, scan_id, scan_configure):
        self._client.scans_api.configure(scan_id, scan_configure)

    def get_agents(self):
        return self._client.agents_api.list().agents

    def get_agent_details(self):
        return self._client.agents_api.details()

