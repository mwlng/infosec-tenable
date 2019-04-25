# -*- coding: utf-8 -*-

"""
Conmmon utilities
"""

import re


def extract_params(kwargs):
    return {k: v for k, v in iter(kwargs.items())
            if (v or v in (0, False)) and k != 'self'}


def snake_to_bigcamel(snake_str):
    words = snake_str.split('_')
    return ''.join(w.title() for w in words)


def snake_to_smallcamel(snake_str):
    words = snake_str.split('_')
    return words[0].lower() + ''.join(w.title() for w in words[1:])


def snake_to_camel(snake_str, small=True):
    if small:
        return snake_to_smallcamel(snake_str)
    return snake_to_bigcamel(snake_str)


def camel_to_snake(camel_str):
    s_str = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s_str).lower()


def generate_params(kwargs, camel_size='small'):
    params = extract_params(kwargs)
    if camel_size.lower() == 'big':
        return dict([(snake_to_bigcamel(k), v) for k, v in params.items()])
    return dict([(snake_to_smallcamel(k), v) for k, v in params.items()])
