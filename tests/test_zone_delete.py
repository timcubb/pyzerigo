#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import zerigo

if __name__ == '__main__':
    zone = zerigo.Zone('test.vmlayers.org')
    try:
        zone.create()
    except zerigo.CreateError:
        pass
    zone.delete()
    try:
        zone.delete()
    except zerigo.DeleteError:
        pass
    else:
        print 'Fail: double delete of a zone is imposible'
        sys.exit(1)
