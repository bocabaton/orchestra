import traceback, logging
from pyengine.lib.dao import DAO
from pyengine.lib.error import *

class Locator():

    logger = logging.getLogger(__name__)

    dao_instance = {}

    def getManager(self, name):
        try:
            manager_module = __import__('pyengine.manager.%s' %name, fromlist=[name])
            return getattr(manager_module, name)()

        except ERROR as e:
            raise e

        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise ERROR_LOCATOR(category='manager', name=name)


    def getDAO(self, name):
        if not self.dao_instance.has_key(name):
            try:
                models_module = __import__('pyengine.models', fromlist=['models'])
                self.dao_instance[name] = DAO(models_module.__dict__[name])

            except ERROR as e:
                raise e

            except Exception as e:
                self.logger.error(traceback.format_exc())
                raise ERROR_LOCATOR(category='dao', name=name)

        return self.dao_instance[name]


    def getInfo(self, name, data, **kwargs):
        try:
            info_module = __import__('pyengine.info.%s' %name, fromlist=[name])

            return getattr(info_module, name)(data, kwargs)

        except ERROR as e:
            raise e

        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise ERROR_LOCATOR(category='info', name=name)
