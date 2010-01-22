#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import zerigo

def list_hosts(zone):
    hosts = zone.list()
    if len(hosts):
        print 'Hosts list for %s:\n * %s' % (zone.name,
            '\n * '.join([host.hostname for host in hosts]))
    else:
        print 'No hosts for %s: ' % zone.name

if __name__ == '__main__':
    zone = zerigo.Zone('test.vmlayers.org')
    try:
        zone.create()
    except zerigo.AlreadyExists:
        pass
    list_hosts(zone)
    zone = zerigo.Zone('vmlayers.org')
    list_hosts(zone)
    zerigo.Zerigo._logger.debug('test success')
