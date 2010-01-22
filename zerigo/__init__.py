#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

import logging

from errors import *
from zerigo import Zerigo, Zone, Host

ZERIGO_USER = 'louis.opter@dotcloud.com'
ZERIGO_PASSWORD = '0ba5f1558ebd401cb14d37ddcf297226'

ZERIGO_LOG_FORMAT = '[%(levelname)s] zerigo: %(message)s.'
ZERIGO_LOG_LEVEL = logging.DEBUG

Zerigo.user = ZERIGO_USER
Zerigo.password = ZERIGO_PASSWORD
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(ZERIGO_LOG_FORMAT))
Zerigo._logger = logging.getLogger('zerigo')
Zerigo._logger.addHandler(handler)
Zerigo._logger.setLevel(ZERIGO_LOG_LEVEL)

Zerigo._logger.debug('using account ' + Zerigo.user + ':' + Zerigo.password)
