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

    """Return a dictionnary of Zone with zonenames in keys for this account"""
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
        list = {}
        zones = tree.getiterator('zone')
        for it in zones:
            name = it.find('domain')
            id = it.find('id')
            if id is None or name is None or id.text is None or name.text is None:
                raise ParseError()
            list[name.text] = Zone(name.text, id.text)

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
        self._id = id

        if not self._id:
            # Try to get the id
            try:
                url = Zerigo._url_api + Zone._url_list.substitute(name=self.name)
                Zerigo._logger.debug('retrieving ' + url)
                zone = self._conn.get(url)
            except restkit.ResourceNotFound:
                self._id = None
                Zerigo._logger.debug('zone ' + self.name + ": doesn't exist (yet)")
                return
            self.__read_id(zone)

        Zerigo._logger.debug('id for zone ' + self.name + ': ' + self._id)

    def __read_id(self, zone):
        assert(zone)

        tree = ElementTree()
        tree.parse(zone.body_file)
        id = tree.find('id')
        if id is None or not id.text:
            self._id = None
            raise ParseError()
        self._id = id.text # used by Zerigo to do almost all operations.

    """Return a dictionnary of Host for this zone (hostname in keys)"""
    def list(self):
        # This list (but up to 300 hosts) is also returned when we get
        # <_url_list>
        if (self._id is None):
            raise NotFound(self.name)

        url = Zerigo._url_api + Zone._url_hosts.substitute(zone_id=self._id)
        Zerigo._logger.debug('retrieving ' + url)
        reply = self._conn.get(url)
        try:
            Zerigo._logger.debug(reply.headers['x-query-count'] + ' host(s) for zone: ' + self.name)
        except:
            raise ParseError()

        tree = ElementTree()
        tree.parse(reply.body_file)
        list = {}
        hosts = tree.getiterator('host')
        for it in hosts:
            id = it.find('id')
            hostname = it.find('hostname')
            type = it.find('host-type')
            data = it.find('data')
            if id is None or type is None or data is None:
                raise ParseError()
            if hostname is None \
                or 'nil' in hostname.attrib and hostname.attrib['nil'] == 'true':
                hostname = '@' # Bind notation
            else:
                hostname = hostname.text
            host = Host(hostname, self.name, id.text, self)
            host.type = type.text
            host.data = data.text
            list[hostname] = host

        return list

    def create(self):
        # do not assert on that, because the id is initialized in the
        # constructor, and the result is not available to the user.
        if (self._id):
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
        Zerigo._logger.debug('zone ' + self.name + ' created with id: ' + self._id)

    def delete(self):
        if (self._id is None):
            raise NotFound(self.name)

        url = Zerigo._url_api + Zone._url_delete.substitute(zone_id=self._id)
        Zerigo._logger.debug('deleting ' + url + ' (' + self.name + ')')
        # will raise an exception in case of problem. Maybe we should at least
        # check for a 404 to be consistent by throwing a zerigo.NotFound ?
        # And to be consistent with create which catch restkit.RequestFailed.
        self._conn.delete(url)
        self._id = None # reset the id, the zone no longer exists

class Host(Zerigo):
    """Used to create or work on a host of the given zone"""

    _url_template = string.Template('/zones/$zone_id/hosts/new.xml')
    _url_create = string.Template('/zones/$zone_id/hosts.xml')
    _url_delete = string.Template('/hosts/$host_id.xml')

    """zonename: name of the zone;
       hostname: name of the host;
       fqdn: hostname + zonename;
       type: 'A', 'CNAME', 'MX', 'AAAA';
       data: ip address for example.

    """
    def __init__(self, hostname, zonename, id=None, zone=None):
        Zerigo.__init__(self)
        # agregate a zone because we need its id
        self.__zone = zone or Zone(zonename)
        if self.__zone._id is None: # the zone doesn't even exists
            raise NotFound(self.__zone.name)
        self.hostname = hostname
        self.type = None
        self.data = None
        self._id = id

        if self._id is None:
            # To be refactored to avoid to fetch the entire zone
            list = self.__zone.list()
            if list.has_key(self.hostname):
                clone = list[self.hostname]
                self._id = clone._id
                self.type = clone.type
                self.data = clone.data
            else:
                Zerigo._logger.debug('host ' + self.fqdn + " doesn't exists (yet)")
        else:
            Zerigo._logger.debug('id for host ' + self.fqdn + ': ' + self._id)

    @property
    def zonename(self):
        return self.__zone.name

    @property
    def fqdn(self):
        return self.hostname + '.' + self.__zone.name

    def create(self):
        assert(self.type in ['A', 'CNAME', 'MX', 'AAAA'])
        assert(self.data)

        if self._id:
            raise AlreadyExists(self.hostname)

        # it works like in Zone.create()
        url = Zerigo._url_api \
              + Host._url_template.substitute(zone_id=self.__zone._id)
        Zerigo._logger.debug('retrieving ' + url)
        template = self._conn.get(url)

        tree = ElementTree()
        tree.parse(template.body_file)
        type = tree.find('host-type')
        hostname = tree.find('hostname')
        data = tree.find('data')
        if type is None or hostname is None or data is None:
            raise ParseError()
        type.text = self.type
        if 'nil' in hostname.attrib:
            del hostname.attrib['nil']
        hostname.text = self.hostname
        if 'nil' in data.attrib:
            del data.attrib['nil']
        data.text = self.data
        form = StringIO.StringIO()
        tree.write(form)
        form = form.getvalue()

        url = Zerigo._url_api + Host._url_create.substitute(zone_id=self.__zone._id)
        # exact same block in Zone; we should find a way to factore this
        try:
            Zerigo._logger.debug('posting ' + url)
            host = self._conn.post(url, body=form)
        except restkit.RequestFailed as errors:
            errors = StringIO.StringIO(errors)
            tree = ElementTree()
            tree.parse(errors)
            errors = [err.text for err in tree.findall('error')]
            raise CreateError(self.name, ', '.join(errors))

        # read the id
        tree = ElementTree()
        tree.parse(host.body_file)
        id = tree.find('id')
        if id  is None or not id.text:
            raise ParseError()
        self._id = id.text
        Zerigo._logger.debug('host ' + self.fqdn + ' created with id: ' + self._id)

    # same block in zone but different url
    def delete(self):
        if self._id is None:
            raise NotFound(self.hostname)

        url = Zerigo._url_api + Host._url_delete.substitute(host_id=self._id)
        Zerigo._logger.debug('deleting ' + url + ' (' + self.hostname + ')')
        self._conn.delete(url)
        self._id = None
