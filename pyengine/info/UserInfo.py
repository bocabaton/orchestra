from pyengine.info import VOInfo
from pyengine.lib.error import *

class UserInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<UserInfo: %s>' %self.vo.user_id 

    def fetchByVO(self):
        if self.checkResponseParams():
            try:
                for p in self.options['res_params']:
                    if p == 'group_name':
                        if self.vo.group:
                            self.output[p] = self.vo.group.name
                        else:
                            self.output[p] = None
                    else:
                        self.output[p] = self.vo.__dict__[p]

            except:
                raise ERROR_INVALID_PARAMETER(key='res_params', value=p)

        else:
            self.output['user_id'] = self.vo.user_id
            self.output['name'] = self.vo.name
            self.output['state'] = self.vo.state
            self.output['email'] = self.vo.email
            self.output['language'] = self.vo.language
            self.output['timezone'] = self.vo.timezone
            self.output['group_id'] = self.vo.group_id

            if self.vo.group:
                self.output['group_name'] = self.vo.group.name
            else:
                self.output['group_name'] = None

            self.output['created'] = self.vo.created
