#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import logging
import string
import StringIO
from xml.etree.ElementTree import ElementTree

import restkit

from errors import ParseError, CreateError, DeleteError

class Zerigo(object):
    """Base object for ZerigoZone and ZerigoHost.

       Zerigo contains the credentials needed to use the API.

    """
    user = None
    password = None

    _logger = None
    _url_api = 'http://ns.zerigo.com/api/1.1'
    _url_zones = '/zones.xml' # zones list

    def __init__(self):
        self._conn = restkit.RestClient(restkit.httpc.HttpClient(),
                                        {'Accept': 'application/xml',
                                         'Content-Type': 'application/xml'})
        self._conn.add_authorization(restkit.httpc.BasicAuth(self.user, self.password))

    """Return a list of ZerigoZone for this account"""
    def list(self):
        url = Zerigo._url_api + Zerigo._url_zones
        Zerigo._logger.debug('retrieving ' + url)
        reply = self._conn.get(url)
        try:
            Zerigo._logger.debug(reply.headers['x-query-count'] + ' zone(s) for account: ' + Zerigo.user)
        except KeyError:
            raise ParseError()

        tree = ElementTree()
        tree.parse(reply.body_file)
        list = []
        zones = tree.getiterator('zone')
        for it in zones:
            name = it.find('domain')
            id = it.find('id')
            if id is None or name is None:
                raise ParseError()
            list.append(Zone(name.text, id.text))

        return list

class Zone(Zerigo):
    """Used to create or work on the given zone"""

    _url_create = '/zones.xml'
    _url_delete = string.Template('/zones/$zone_id.xml')
    _url_list = string.Template('/zones/$name.xml') # zone attributes
    _url_template = '/zones/new.xml'

    """name: domain name of the zone

    """
    def __init__(self, name, id=None):
        assert(name)

        Zerigo.__init__(self)
        self.name = name
        self.__id = id

        if not self.__id:
            # Try to get it
            try:
                url = Zerigo._url_api + Zone._url_list.substitute(name=self.name)
                Zerigo._logger.debug('retrieving ' + url)
                zone = self._conn.get(url)
            except restkit.ResourceNotFound:
                self.__id = None
                Zerigo._logger.debug('zone ' + self.name + ": doesn't exist (yet)")
                return
            self.__read_id(zone)

        Zerigo._logger.debug('id for zone ' + self.name + ': ' + self.__id)

    def __read_id(self, zone):
        assert(zone)

        tree = ElementTree()
        tree.parse(zone.body_file)
        id = tree.find('id')
        if id is None or not id.text:
            self.__id = None
            raise ParseError()
        self.__id = id.text # used by Zerigo to do almost all operations.

    """Return a list of ZerigoHost for this zone"""
    def list(self):
        pass

    def create(self):
        # do not assert on that, because the id is initialized in the
        # constructor, and the result is not available to the user.
        if (self.__id):
            raise CreateError(self.name, 'Domain already exists')

        # get the template, can be cached
        url = Zerigo._url_api + Zone._url_template
        Zerigo._logger.debug('retrieving ' + url)
        template = self._conn.get(url)

        # parse it and create the form to post
        tree = ElementTree()
        tree.parse(template.body_file)
        domain = tree.find('domain')
        if domain is None:
            raise ParseError()
        del domain.attrib['nil']
        domain.text = self.name
        form = StringIO.StringIO()
        tree.write(form)
        form = form.getvalue()

        # post it and read reply
        url = Zerigo._url_api + Zone._url_create
        try:
            Zerigo._logger.debug('posting ' + url)
            zone = self._conn.post(url, body=form)
        except restkit.RequestFailed as errors:
            errors = StringIO.StringIO(errors)
            tree = ElementTree()
            tree.parse(errors)
            errors = [err.text for err in tree.findall('error')]
            raise CreateError(self.name, ', '.join(errors))

        self.__read_id(zone)
        Zerigo._logger.debug('zone ' + self.name + ' created with id: ' + self.__id)

    def delete(self):
        if (self.__id is None):
            raise DeleteError(self.name, "Domain doesn't exist")

        url = Zerigo._url_api + Zone._url_delete.substitute(zone_id=self.__id)
        Zerigo._logger.debug('deleting ' + url + ' (' + self.name + ')')
        self._conn.delete(url) # will raise an exception in case of problem
        self.__id = None # reset the id, the zone no longer exists

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
