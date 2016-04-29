import traceback, logging
from django.views.generic import View
from pyengine.lib.error import *
from pyengine.lib.router import Router
from pyengine.lib.parser import Parser
from pyengine.lib.auth import Auth
from pyengine.lib.response import Response
from pyengine.lib.plugin import Plugin

class Request(View):

    logger = logging.getLogger(__name__)
    router = Router()
    parser = Parser()
    auth = Auth()
    plugin = Plugin()
    response = Response()

    def dispatch(self, request, *args, **kwargs):
        api = None
        api_accept = 'application/json'

        try:
            # 1. RESTful URL Check 
            api_request = self.router.match(request)
            api_class = api_request['meta']['api_class'] 
            api_version = api_request['meta']['api_version'] 

            # 2. Get Request Parameter
            api_request = self.parser.getParams(request, api_request)
            api_accept = api_request['meta']['accept']

            # 3. API Auth
            api_request = self.auth.verify(api_request)

            # 4. Preload Plugins
            try:
                api_module = __import__('pyengine.api.%s.%s' %(api_version, api_class), fromlist=[api_class])

            except Exception as e:
                self.logger.error(traceback.format_exc()) 
                raise ERROR_UNKNOWN_ERROR(message = e)

            # 5. Preload Plugins
            api_request = self.plugin.preload(api_request)

            # 5. Execute API
            api = getattr(api_module, api_class)(api_request)
            result = api.execute()

            # 6. Success Plugins
            result = self.plugin.success(api_request, result)

            return self.response.success(result, api_accept)

        except ERROR as e:
            if api != None:
                # Rollback API & Error Plugins
                api.rollback()
                self.plugin.error(api_request, e)

            self.logger.error(e.message['message'])

            return self.response.error(e, api_accept)

        except Exception as e:
            error = ERROR_UNKNOWN_ERROR(message=e)

            if api != None:
                # Rollback API & Error Plugins
                api.rollback()
                self.plugin.error(api_request, error)

            self.logger.error(traceback.format_exc())
            self.logger.error(error.message['message'])

            return self.response.error(error, api_accept)
