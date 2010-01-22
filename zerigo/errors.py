#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import logging

class ZerigoException(Exception):
    """Inherited by all zerigo exceptions classes"""

class ParseError(ZerigoException):
    """Raised when the received xml is invalid"""

    def __str__(self):
        return 'Unable to decode the response.'

class AlreadyExists(ZerigoException):
    """Raised when you try to create an host or zone which already exists"""

    def __init__(self, name):
        self.__msg = name + ': already exists.'

    def __str__(self):
        return self.__msg

class NotFound(ZerigoException):
    """Raised when you try to do something which doesn't exists"""

    def __init__(self, name):
        self.__msg = name + ": doesn't exists."

    def __str__(self):
        return self.__msg

class CreateError(ZerigoException):
    """Generic error raised when an host or zone creation fail"""

    def __init__(self, name, msg):
        self.__msg = name + ': ' + (msg or 'unknown error') + '.'

    def __str__(self):
        return self.__msg

class DeleteError(ZerigoException):
    """Generic error raised when an host or zone deletion fail"""

    def __init__(self, name, msg):
        self.__msg = name + ': ' + (msg or 'unknown error') + '.'

    def __str__(self):
        return self.__msg
