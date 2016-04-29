from pyengine.info import VOInfo
from pyengine.lib.error import *

class ProductDetailInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<ProductDetailInfo: %s>' %self.vo.uuid 

    def fetchByVO(self):
        self.output['uuid'] = self.vo.uuid
        self.output['product_id'] = self.vo.product_id

        if self.vo.email:
            self.output['email'] = self.vo.email
        else:
            self.output['email'] = ''

        if self.vo.support_link:
            self.output['support_link'] = self.vo.support_link
        else:
            self.output['support_link'] = ''

        if self.vo.support_description:
            self.output['support_description'] = self.vo.support_description
        else:
            self.output['support_description'] = ''
