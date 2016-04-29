import logging
from pyengine.lib.error import *
from pyengine.lib.locator import Locator

class Plugin(object):
    """
    Plugin class in basic interface
    Every XXXPlugin has to inherit Plugin
    """

    logger = logging.getLogger(__name__)
    locator = Locator()

    def preload(self, api_request):
        """
        Override in plugin preload process
        """
        return api_request

    def success(self, api_request, result):
        """
        Override in plugin success process
        """
        return result

    def error(self, api_request, error):
        """
        Override in plugin error process
        """
        pass
