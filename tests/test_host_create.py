#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import zerigo

if __name__ == '__main__':
    try:
        host = zerigo.Host('www', 'test.vmlayers.org')
    except zerigo.NotFound: # zone not found
        zone = zerigo.Zone('test.vmlayers.org')
        zone.create()
        host = zerigo.Host('www', 'test.vmlayers.org')
    host.type = 'A'
    host.data = '82.66.148.158'
    host.create()
    try:
        host = zerigo.Host('www', 'test.vmlayers.org')
        host.create()
    except:
        pass
    else:
        zerigo.Zerigo._logger.debug('test fail: double create of a host is impossible')
        sys.exit(1)
    zerigo.Zerigo._logger.debug('test success')
