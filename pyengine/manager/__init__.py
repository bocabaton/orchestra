import logging
from pyengine.lib.error import *
from pyengine.lib.locator import Locator

class Manager(object):
    """
    Manager class is basic Interface
    Every XXXManager has to inherit Manager
    """

    logger = logging.getLogger(__name__)
    locator = Locator()
