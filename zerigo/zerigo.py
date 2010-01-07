#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import logging
import string
import StringIO
from xml.etree.ElementTree import ElementTree

import restkit

from errors import ParseError

class Zerigo(object):
    """Base object for ZerigoZone and ZerigoHost.

       Zerigo contains the credentials needed to use the API.

    """
    user = None
    password = None

    _url_api = 'http://ns.zerigo.com/api/1.1'
    _logger = None

    def __init__(self):
        self._conn = restkit.RestClient(restkit.httpc.HttpClient(),
                                        {'Accept': 'application/xml'})
        self._conn.add_authorization(restkit.httpc.BasicAuth(self.user, self.password))
        Zerigo._logger.debug('using account ' + self.user + ':' + self.password)

    """Return a list of ZerigoZone for this account"""
    def list(self):
        xml = self._conn.get(Zerigo._url_api + '/zones.xml')
        print xml.body

class Zone(Zerigo):
    """Used to create or work on the given zone"""

    _url_list = string.Template('/zones/$name.xml')

    """name: domain name of the zone

    """
    def __init__(self, name):
        assert(name)

        Zerigo.__init__(self)
        self.name = name
        self.__id = None # used by Zerigo to do almost all operations.

        url = Zerigo._url_api + Zone._url_list.substitute(name=self.name)
        Zerigo._logger.debug('retrieving ' + url)
        zone = self._conn.get(url)
        tree = ElementTree()
        tree.parse(StringIO.StringIO(zone.body))
        id = tree.find('id')
        if id == None or not id.text:
            raise ParseError()
        self.__id = id.text
        Zerigo._logger.debug('id for zone: ' + self.name + ': ' + self.__id)

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
