from pyengine.info import VOInfo
from pyengine.lib.error import *

class GroupInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<GroupInfo: %s>' %self.vo.user_id 

    def fetchByVO(self):
        if self.checkResponseParams():
            try:
                for p in self.options['res_params']:
                    if p == 'user_count':
                        self.output['user_count'] = self.vo.user_set.all().count()

                    else:
                        self.output[p] = self.vo.__dict__[p]

            except:
                raise ERROR_INVALID_PARAMETER(key='res_params', value=p)

        else:
            self.output['id'] = self.vo.uuid
            self.output['name'] = self.vo.name
            self.output['description'] = self.vo.description
            self.output['user_count'] = self.vo.user_set.all().count()
            self.output['created'] = self.vo.created
