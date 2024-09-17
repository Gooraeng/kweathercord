"""
Korean Weather Tool For Discord Bot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2024-present Gooraeng
:license: MIT, see LICENSE.txt for more datils.

"""


__title__ = 'kweathercord'
__author__ = 'Gooraeng'
__license__ = 'MIT'
__copyright__ = 'Copyright 2024-present Gooraeng'
__version__ = '0.1.2'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import logging
from typing import NamedTuple, Literal

from .client import *
from .enums import *
from .exception import *
from .model import *
from .utils import *
from .view import *


class Version(NamedTuple):
    major : int
    minor : int
    micro : int
    release : Literal['alpha', 'beta', 'candidate', 'final']
    serial : int

version_info = Version(major=0, minor=1, micro=2, release='final', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())

del logging, NamedTuple, Literal, Version