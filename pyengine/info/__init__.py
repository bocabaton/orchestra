import logging
import pytz
import uuid
import abc
from datetime import datetime
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.lib.locator import Locator

class Info(object):

    logger = logging.getLogger(__name__)
    locator = Locator()

    GLOBAL_CONF = config.getGlobalConfig()

    def __init__(self, options):
        self.options = options
        self.output = {}

    def checkResponseParams(self):
        if len(self.options.get('res_params', [])) > 0:
            return True
        else:
            return False

    def _recursionInfo(self, key, value, tz): 
        # UUID Type to String
        if type(value) == uuid.UUID:
            return str(value)

        # Time Conversion
        elif key in self.GLOBAL_CONF['DATETIME_FIELDS']: 
            if value != None:
                value = value.replace(tzinfo=pytz.utc).astimezone(tz)
                return value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return ''

        # Instance
        elif isinstance(value, Info) == True:
            return value.result(tz)

        # List
        elif type(value) == type(list()):
            # Default
            list_output = []
            for v in value:
                if type(v) == type(dict()):
                    dic_output = {}
                    for k in v:
                        dic_output[k] = self._recursionInfo(k, v[k], tz)

                    list_output.append(dic_output)

                elif isinstance(v, Info) == True:
                    list_output.append(v.result(tz))

                else:
                    list_output.append(v)

            return list_output

        # Dictionary
        elif type(value) == type(dict()):
            output = {}
            for k in value:
                output[k] = self._recursionInfo(k, value[k], tz)

            return output

        # No Change
        else:
            return value

    def result(self, timezone=None): 
        if timezone == None:
            timezone = self.GLOBAL_CONF['DEFAULT_TIMEZONE']

        tz = pytz.timezone(timezone)

        to_string = {}
        for k in self.output:
            to_string[k] = self._recursionInfo(k, self.output[k], tz)

        return to_string


class DataInfo(Info):
    __metaclass__ = abc.ABCMeta

    def __init__(self, data, options):
        Info.__init__(self, options)
        self.data = data
        self.fetchByData()

    @abc.abstractmethod
    def fetchByData(self):
        """
        Fetch needed data from data paremeter
        """
        pass


class VOInfo(Info):
    __metaclass__ = abc.ABCMeta

    def __init__(self, vo, options):
        Info.__init__(self, options)
        self.vo = vo
        self.fetchByVO()

    def fetchByVO(self):
        """
        Fetch needed data from vo(value object)
        """
        pass
