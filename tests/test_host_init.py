#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import zerigo

if __name__ == '__main__':
    host = zerigo.Host('www', 'test.vmlayers.org')
    zerigo.Zerigo._logger.debug('hostname = ' + host.hostname)
    zerigo.Zerigo._logger.debug('zonename = ' + host.zonename)
    zerigo.Zerigo._logger.debug('fqdn = ' + host.fqdn)
    host = zerigo.Host('foo', 'test.vmlayers.org')
    zerigo.Zerigo._logger.debug('hostname = ' + host.hostname)
    zerigo.Zerigo._logger.debug('zonename = ' + host.zonename)
    zerigo.Zerigo._logger.debug('fqdn = ' + host.fqdn)
    zerigo.Zerigo._logger.debug('test success')
