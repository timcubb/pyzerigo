#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import zerigo

if __name__ == '__main__':
    zone = zerigo.Zone('test.vmlayers.org')
    try:
        zone.delete()
    except:
        pass
    zone.create()
    try:
        zone.create()
    except:
        pass
    else:
        zerigo.Zerigo._logger.debug('test fail: double create of a zone is impossible')
        sys.exit(1)
    zerigo.Zerigo._logger.debug('test success')
