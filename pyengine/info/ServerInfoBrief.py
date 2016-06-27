from pyengine.info import DataInfo
from pyengine.lib.error import *

class ServerInfoBrief(DataInfo):
    def __init__(self, data, options):
        super(self.__class__, self).__init__(data, options)
        self.fetchByData()

    def __repr__(self):
        return '<ServerInfoBrief: %s>' % self.data['server_id']

    def fetchByVO(self):
        self.output = self.data
