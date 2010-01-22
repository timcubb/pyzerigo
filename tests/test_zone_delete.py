#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import zerigo

if __name__ == '__main__':
    zone = zerigo.Zone('test.vmlayers.org')
    try:
        zone.create()
    except zerigo.AlreadyExists:
        pass
    zone.delete()
    try:
        zone.delete()
    except zerigo.NotFound:
        pass
    else:
        zerigo.Zerigo._logger.debug('test fail: double delete of a zone is imposible')
        sys.exit(1)
    zerigo.Zerigo._logger.debug('test success')
