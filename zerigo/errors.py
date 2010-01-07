#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import logging

class ZerigoException(Exception):
    """Inherited by all zerigo exceptions classes"""

class ParseError(ZerigoException):
    """Raised when the received xml is invalid"""
