#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import zerigo

if __name__ == '__main__':
    account = zerigo.Zerigo()
    zones = account.list()
    print 'Zones list:\n * ' + '\n * '.join([zone.name for zone in zones])
