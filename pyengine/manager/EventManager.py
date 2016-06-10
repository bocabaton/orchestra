from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class EventManager(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def addEvent(self, user_id, msg, group_id=""):
        event_dao = self.locator.getDAO('event') 

        dic = {}
        dic['user_id'] = user_id
        dic['msg'] = msg
        dic['group_id'] = group_id

        event = event_dao.insert(dic)

        return True

    def listEvents(self, search, search_or, sort, page, res_params):
        event_dao = self.locator.getDAO('event')

        output = []
        (events, total_count) = event_dao.select(search=search, search_or=search_or, sort=sort, page=page)

        for event in events:
            event_info = self.locator.getInfo('EventInfo', event)
            output.append(event_info)

        return (output, total_count)

