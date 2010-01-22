#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import zerigo

if __name__ == '__main__':
    zone = zerigo.Zone('vmlayers.org')
    zone = zerigo.Zone('notfound.com')
    zerigo.Zerigo._logger.debug('test success')
