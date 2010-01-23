#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import zerigo

if __name__ == '__main__':
    try:
        host = zerigo.Host('www', 'test.vmlayers.org')
    except zerigo.NotFound:
        zone = zerigo.Zone('test.vmlayers.org')
        zone.create()
    if host.data is None: # the host doesn't exists
        host.data = '82.66.148.158'
        host.type = 'A'
        host.create()
    host.delete()
    try:
        host = zerigo.Host('www', 'test.vmlayers.org')
        host.delete()
    except zerigo.NotFound:
        pass
    else:
        zerigo._logger.debug('test fail: double delete of a host is impossible')
        sys.exit(1)
    zerigo.Zerigo._logger.debug('test succes')
