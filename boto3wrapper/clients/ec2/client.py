# -*- coding: utf-8 -*-

"""
EC2 client class
"""

from boto3wrapper.base import *
from boto3wrapper.utils import *


class EC2Client(AWSClient):

    def __init__(self, 
                 region_name=None, 
                 profile_name=None,
                 access_key=None, secret_key=None):
        super(EC2Client, self).__init__("ec2", 
                                        region_name, 
                                        profile_name,
                                        access_key, secret_key)
        self.camel_size = 'big'
                             

    def describe_instances(self, instance_ids, dry_run=False, 
                           filters=None, next_token=None):
        inputs = locals()
        params = generate_params(inputs, self.camel_size)
        return self._cli.describe_instances(**params)


    def describe_all_instances(self, max_results, dry_run=False,
                               filters=None, next_token=None):
        inputs = locals()
        params = generate_params(inputs, self.camel_size)
        return self._cli.describe_instances(**params)

    def describe_instance_status(self, instance_ids, dry_run=False, 
                                 filters=None, include_all_instances=False, 
                                 next_token=None):
        inputs = locals()
        params = generate_params(inputs, self.camel_size)
        return self._cli.describe_instance_status(**params)
