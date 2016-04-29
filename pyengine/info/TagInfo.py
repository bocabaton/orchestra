from pyengine.info import VOInfo
from pyengine.lib.error import *

class TagInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<TagInfo: %s>' %self.vo.uuid 

    def fetchByVO(self):
        self.output['uuid'] = self.vo.uuid
        self.output['product_id'] = self.vo.product_id
        self.output['key'] = self.vo.key
        self.output['value'] = self.vo.value
