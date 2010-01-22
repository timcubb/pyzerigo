#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import logging

class ZerigoException(Exception):
    """Inherited by all zerigo exceptions classes"""

class ParseError(ZerigoException):
    """Raised when the received xml is invalid"""

class CreateError(ZerigoException):
    """Raised when an host or zone creation fail"""

    def __init__(self, name, msg):
        self.__msg = name + ': ' + (msg or 'Unknown error') + '.'

    def __str__(self):
        return self.__msg

class DeleteError(ZerigoException):
    """Raised when an host or zone deletion fail"""

    def __init__(self, name, msg):
        self.__msg = name + ': ' + (msg or 'Unknown error') + '.'

    def __str__(self):
        return self.__msg
