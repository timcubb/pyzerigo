#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import zerigo

if __name__ == '__main__':
    account = zerigo.Zerigo()
    zones = account.list()
    if len(zones):
        print 'Zones list:\n * ' + '\n * '.join([zone.name for zone in zones])
    else:
        print 'No zones on this account.'
    zerigo.Zerigo._logger.debug('test success')
