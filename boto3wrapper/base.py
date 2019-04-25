# -*- coding: utf-8 -*-

"""
AWS base classes
"""

import json
import datetime
import collections
import boto3

from .utils import generate_params
from .utils import snake_to_camel
from .utils import camel_to_snake


AWS_SERVICES = [
    "sts",
    "s3",
    "iam",
    "ec2",
    "alb",
    "elb",
    "ecr",
    "ecs",
    "sns",
    "ses",
    "ssm",
    "emr",
    "lambda",
    "route53",
    "autoscaling",
    "cloudformation",
    "redshift"
]


class ServiceNotSupportException(Exception):
    def __init__(self, service_type):
        self.service_type = service_type
        self.message = "Service {} not support".format(service_type)
        super(ServiceNotSupportException, self).__init__()


class AWSClient(object):
    def __init__(self, service_name, region_name=None, profile_name=None,
                 access_key=None, secret_key=None):
        if service_name not in AWS_SERVICES:
            raise ServiceNotSupportException(service_name)
        self._service_name = service_name
        self._region_name = region_name
        self._profile_name = profile_name
        self._access_key = access_key
        self._secret_key = secret_key
        self._cli = None

    def __enter__(self):
        sess_params = {}
        if self._region_name:
            sess_params['region_name'] = self._region_name
        if self._profile_name:
            sess_params['profile_name'] = self._profile_name
        if self._access_key and self._secret_key:
            sess_params['aws_access_key_id'] = self._access_key
            sess_params['aws_secret_access_key'] = self._secret_key
        if sess_params:
            self._cli = boto3.Session(**sess_params).client(self._service_name)
        else:
            self._cli = boto3.client(self._service_name)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._cli = None

    def generate_presigned_url(self, client_method, params=None,
                               expires_in=3600, http_method=None):
        inputs = locals()
        params = generate_params(inputs)
        return self._cli.generate_presigned_url(**params)

    def can_paginate(self, op_name):
        return self._cli.can_paginate(op_name)

    def get_paginator(self, op_name):
        return self._cli.get_paginator(op_name)

    def get_waiter(self, waiter_name):
        return self._cli.get_waiter(waiter_name)


class AWSResource(object):
    def __init__(self, service_name, region_name=None,
                 profile_name=None, access_key=None, secret_key=None):
        if service_name not in AWS_SERVICES:
            raise ServiceNotSupportException(service_name)
        self._service_name = service_name
        self._region_name = region_name
        self._profile_name = profile_name
        self._access_key = access_key
        self._secret_key = secret_key
        sess_params = {}
        if self._region_name:
            sess_params['region_name'] = self._region_name
        if self._profile_name:
            sess_params['profile_name'] = self._profile_name
        if self._access_key and self._secret_key:
            sess_params['aws_access_key_id'] = self._access_key
            sess_params['aws_secret_access_key'] = self._secret_key
        if sess_params:
            self._sess = boto3.Session(**sess_params).resource(self._service_name)
        else:
            self._sess = boto3.resource(self._service_name)


class AWSObject(object):

    def __init__(self):
        self._options = []
        self._resource_type = None

    def __repr__(self):
        return "{clazz}::{obj}".format(clazz=self.__class__.__name__,
                                       obj=self.to_json(minimal=False))

    def json_repr(self, minimal=False, camel_size='small'):
        if minimal:
            if camel_size == 'small':
                return {snake_to_camel(k): v for k, v in vars(self).items() if (v or v is False or v == 0) and (not k.startswith('_'))}
            else:
                return {snake_to_camel(k, small=False): v for k, v in vars(self).items() if (v or v is False or v == 0) and (not k.startswith('_'))}
        else:
            if camel_size == 'small':
                return {snake_to_camel(k): v for k, v in vars(self).items() if not k.startswith('_')}
            else:
                return {snake_to_camel(k, small=False): v for k, v in vars(self).items() if not k.startswith('_')}

    def __str__(self):
        ret = ""
        for k, v in vars(self).items():
            if not k.startswith('_'):
                if v or v in (False, 0):
                    ret += "%s:\t\t%s\n" % (k, v)
        return ret

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def set_options(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._options:
                setattr(self, k, v)

    @classmethod
    def from_json(cls, attributes):
        return cls(**{k: v for k, v in attributes.items()})

    def to_json(self, minimal=True):
        if minimal:
            return json.dumps(self.json_repr(minimal=True),
                              cls=AWSResourceObjectMinimalJsonEncoder,
                              sort_keys=True)
        return json.dumps(self.json_repr(),
                          cls=AWSResourceObjectJsonEncoder, sort_keys=True)

    def get_snake_properties(self, minimal=False):
        if minimal:
            return {camel_to_snake(k): v for k, v in vars(self).items()
                    if (v or v is False or v == 0) and (not k.startswith('_'))}
        return {camel_to_snake(k): v for k, v in vars(self).items() if not k.startswith('_')}


def is_stringy(obj):
    return isinstance(obj, str)


class AWSResourceObjectJsonEncoder(json.JSONEncoder):

    """Custom JSON encoderfor aws resource object serialization."""

    def default(self, obj):
        if hasattr(obj, 'json_repr'):
            return self.default(obj.json_repr())

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if isinstance(obj, collections.Iterable) and not is_stringy(obj):
            try:
                return {k: self.default(v) for k, v in obj.items()}
            except AttributeError:
                return [self.default(e) for e in obj]
        return obj


class AWSResourceObjectMinimalJsonEncoder(json.JSONEncoder):

    """Custom JSON encoder for aws resource object minimal serialization."""

    def default(self, obj):
        if hasattr(obj, 'json_repr'):
            return self.default(obj.json_repr(minimal=True))

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if isinstance(obj, collections.Iterable) and not is_stringy(obj):
            try:
                return {k: self.default(v) for k, v in obj.items() if v or v in (False, 0)}
            except AttributeError:
                return [self.default(e) for e in obj if e or e in (False, 0)]
        return obj
