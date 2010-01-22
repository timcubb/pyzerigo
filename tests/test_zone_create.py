#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import zerigo

if __name__ == '__main__':
    zone = zerigo.Zone('test.vmlayers.org')
    zone.create()
    try:
        zone.create()
    except zerigo.CreateError:
        pass
    else:
        print 'Fail: double create of a zone is impossible'
        sys.exit(1)
