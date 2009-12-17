#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys
import restkit

ZERIGO_USER = 'louis.opter@dotcloud.com'
ZERIGO_PASSWORD = '0ba5f1558ebd401cb14d37ddcf297226'

class ZerigoException(Exception):

    def __init__(self, value):
        self.__value = value

    def __str__(self):
        return 'ZerigoException: ' + repr(value)

class Zerigo(object):
    """Base object for ZerigoZone and ZerigoHost

       Zerigo contains the credentials needed to use the API

    """
    user = None
    password = None
    api_url = 'http://ns.zerigo.com/api/1.1'

    def __init__(self):
        if (not self.user or not self.password):
            raise ZerigoException('Bad username or password')
        self.conn = restkit.RestClient(
                restkit.httpc.HttpClient(),
                {'Accept': 'application/xml'}
                )
        self.conn.add_authorization(restkit.httpc.BasicAuth((self.user, self.password)))

    """List all zones for this account"""
    def list(self):
        xml = self.conn.get(self.api_url + '/zones.xml')
        print xml

class ZerigoZone(Zerigo):
    """Used to work on the given zone"""

    def __init__(self, name):
        Zerigo.__init__(self)
        self.domain = None

    """List hosts in the zone"""
    def list(self):
        pass

    def create(self):
        pass

    def delete(self):
        pass

class ZerigoHost(Zerigo):
    """Used to work on a host of the given zone"""

    def __init__(self, zone, name):
        pass

    """List host attributes"""
    def list(self):
        pass

    def create(self):
        pass

    def delete(self):
        pass

if __name__ == '__main__':
    Zerigo.user = ZERIGO_USER
    Zerigo.password = ZERIGO_PASSWORD
    account = Zerigo()
    account.list()
