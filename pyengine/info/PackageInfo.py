from pyengine.info import VOInfo
from pyengine.lib.error import *

class PackageInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<PackageInfo: %s>' %self.vo.package_id

    def fetchByVO(self):
        self.output['package_id'] = self.vo.package_id
        self.output['product_id'] = self.vo.product_id
        self.output['version'] = self.vo.version
        self.output['created'] = self.vo.created

        if self.vo.pkg_type:
            self.output['pkg_type'] = self.vo.pkg_type
        else:
            self.output['pkg_type'] = ''

        if self.vo.template:
            self.output['template'] = self.vo.template
        else:
            self.output['template'] = ''

        if self.vo.description:
            self.output['description'] = self.vo.description
        else:
            self.output['description'] = ''
