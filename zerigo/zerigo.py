#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys
import logging
import xml.etree.ElementTree

import restkit

class Exception(Exception):

    def __init__(self, value):
        self.__value = value

    def __str__(self):
        return 'ZerigoException: ' + repr(value)

class Zerigo(object):
    """Base object for ZerigoZone and ZerigoHost.

       Zerigo contains the credentials needed to use the API.

    """
    user = None
    password = None
    api_url = 'http://ns.zerigo.com/api/1.1'
    logger = None

    def __init__(self):
        self._conn = restkit.RestClient(restkit.httpc.HttpClient(),
                                        {'Accept': 'application/xml'})
        self._conn.add_authorization(restkit.httpc.BasicAuth(self.user, self.password))

    """Return a list of ZerigoZone for this account"""
    def list(self):
        xml = self._conn.get(self.api_url + '/zones.xml')
        print xml.body

class Zone(Zerigo):
    """Used to create or work on the given zone"""

    """name: domain name of the zone

    """
    def __init__(self, name):
        Zerigo.__init__(self)
        self.name = name
        self.__id = None # used by Zerigo to do almost all operations.

    """Return a list of ZerigoHost for this zone"""
    def list(self):
        pass

    def create(self):
        pass

    def delete(self):
        pass

class Host(Zerigo):
    """Used to create or work on a host of the given zone"""

    """zone: domain name of the zone;
       type: A, CNAME;
       hostname: name of the host;
       data: ip address for example.

    """
    def __init__(self, zone):
        Zerigo.__init__(self)
        self.type = None
        self.hostname = None
        self.data = None
        self.__zone_id = None
        self.__id = None

    def create(self):
        pass

    def delete(self):
        pass
