import logging
import json
from pyengine.lib.error import *

class Parser:
    
    logger = logging.getLogger(__name__)

    CONTENT_TYPES = ['application/json', 'application/xml', 'application/x-www-form-urlencoded']
    ACCEPTS = ['application/json', 'application/xml', 'text/plain', 'text/html']

    def getParams(self, request, api_request):
        if request.method in ['GET', 'DELETE']:
            data = request.GET.dict()

        elif request.method in ['POST', 'PUT']:
            data = self._parseParams(request)

        else:
            raise ERROR_INVALID_HTTP_METHOD(method=request.method)

        # Merge REST URL & Query Parameter
        api_request['params'] = dict(data.items() + api_request['params'].items())

        # Get XAuth Token
        if request.META.has_key('HTTP_X_AUTH_TOKEN'):
            api_request['meta']['xtoken'] = request.META['HTTP_X_AUTH_TOKEN']

        # Get Accept Header
        api_request['meta']['accept'] = self._getAccept(request)

        return api_request

    def _parseParams(self, request):
        content_type = self._getContentType(request)

        if content_type == 'application/json':
            if request.body.strip() == '':
                return {}
            else:
                return self._jsonDecode(request.body) 

        else:
            raise ERROR_INVALID_CONTENT_TYPE(supported_types='json')

    def _getContentType(self, request):
        if request.META.has_key('CONTENT_TYPE'):
            for content_type in request.META['CONTENT_TYPE'].split(';'):
                if content_type in self.CONTENT_TYPES:
                    return content_type

        return 'unknown'

    def _getAccept(self, request):
        if request.META.has_key('HTTP_ACCEPT'):
            for accept in request.META['HTTP_ACCEPT'].split(';'):
                if accept in self.ACCEPTS:
                    return accept

        return 'unknown'

    def _jsonDecode(self, res_json):
        try:
            res_params = json.loads(res_json)
            return res_params

        except Exception as e:
            self.logger.error('JSON Decode Error: %s' %(e))
            raise ERROR_INVALID_JSON_FORMAT()
