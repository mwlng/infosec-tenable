# -*- coding: utf-8 -*-

"""
EC2 metadata
"""

import urllib.request

def get_meta_data(key):
    url_path = 'http://169.254.169.254/latest/meta-data/' + key
    return urllib.request.urlopen(url_path).read().decode()


def get_instance_id():
    return get_meta_data('instance-id')


def get_availability_zone():
    return get_meta_data('placement/availability-zone')


def get_current_region():
    zone = get_availability_zone()
    return zone[:-1] 

