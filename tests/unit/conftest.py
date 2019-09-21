# -*- coding: utf-8 -*-
""" pytest setup """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import dirname, relpath


def pytest_itemcollected(item):
    """ Prettier test names. """
    name = item.originalname or item.name
    if name.startswith('test_'):
        name = name[5:]

    name = name.replace('_', ' ').strip()
    name = name[0].upper() + name[1:]

    rel_path = relpath(item.fspath.strpath, dirname(item.fspath.dirname))
    item._nodeid = '{location:50} {name}'.format(
        name=name,
        location='{}:{}'.format(rel_path, item.location[1]),
    )
