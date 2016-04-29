from pyengine.info import VOInfo
from pyengine.lib.error import *

class ServerInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<ServerInfo: %s>' %self.vo.server_id 

    def fetchByVO(self):
        self.output['server_id'] = self.vo.server_id
        self.output['name'] = self.vo.name
        self.output['zone_id'] = self.vo.zone_id
