from pyengine.info import VOInfo
from pyengine.lib.error import *

class PortfolioInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<PortfolioInfo: %s>' %self.vo.portfolio_id 

    def fetchByVO(self):
        self.output['portfolio_id'] = self.vo.portfolio_id
        self.output['name'] = self.vo.name
        self.output['owner'] = self.vo.owner
        self.output['created'] = self.vo.created

        if self.vo.description:
            self.output['description'] = self.vo.description
        else:
            self.output['description'] = ''
