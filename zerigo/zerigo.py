#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import sys

import logging
import string
import StringIO
from xml.etree.ElementTree import ElementTree

import restkit

from errors import ParseError, CreateError, AlreadyExists, NotFound

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
    _url_hosts = string.Template('/zones/$zone_id/hosts.xml') # hosts list
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
            # Try to get the id
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
        # This list (but up to 300 hosts) is also returned when we get
        # <_url_list>
        if (self.__id is None):
            raise NotFound(self.name)

        url = Zerigo._url_api + Zone._url_hosts.substitute(zone_id=self.__id)
        Zerigo._logger.debug('retrieving ' + url)
        reply = self._conn.get(url)
        try:
            Zerigo._logger.debug(reply.headers['x-query-count'] + ' host(s) for zone: ' + self.name)
        except:
            raise ParseError()

        tree = ElementTree()
        tree.parse(reply.body_file)
        list = []
        hosts = tree.getiterator('host')
        for it in hosts:
            id = it.find('id')
            hostname = it.find('hostname')
            type = it.find('host-type')
            data = it.find('data')
            if id is None or type is None or data is None:
                raise ParseError()
            host = Host(self.name, id.text, self.__id)
            host.type = type.text
            host.data = data.text
            if hostname is None \
                or 'nil' in hostname.attrib and hostname.attrib['nil'] == 'true':
                host.hostname = '@' # Bind notation
            else:
                host.hostname = hostname.text
            list.append(host)

        return list

    def create(self):
        # do not assert on that, because the id is initialized in the
        # constructor, and the result is not available to the user.
        if (self.__id):
            raise AlreadyExists(self.name)

        # get the template, can be cached
        url = Zerigo._url_api + Zone._url_template
        Zerigo._logger.debug('retrieving ' + url)
        template = self._conn.get(url)

        # parse and use it to create the form to post
        tree = ElementTree()
        tree.parse(template.body_file)
        domain = tree.find('domain')
        if domain is None:
            raise ParseError()
        if 'nil' in domain.attrib:
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
            raise NotFound(self.name)

        url = Zerigo._url_api + Zone._url_delete.substitute(zone_id=self.__id)
        Zerigo._logger.debug('deleting ' + url + ' (' + self.name + ')')
        # will raise an exception in case of problem. Maybe we should at least
        # check for a 404 to be consitent by throwing a zerigo.NotFound ? :
        self._conn.delete(url)
        self.__id = None # reset the id, the zone no longer exists

class Host(Zerigo):
    """Used to create or work on a host of the given zone"""

    """zone: name of the zone;
       type: A, CNAME;
       hostname: name of the host;
       data: ip address for example.

    """
    def __init__(self, zone, id=None, zone_id=None):
        Zerigo.__init__(self)
        self.type = None
        self.hostname = None
        self.data = None
        self.zone = zone
        self.__zone_id = zone_id
        self.__id = id

    def create(self):
        pass

    def delete(self):
        pass
