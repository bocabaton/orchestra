import logging
import json
from django.http import HttpResponse
from pyengine.lib.error import *

class Response:
    
    logger = logging.getLogger(__name__)

    def error(self, error_obj, accept):
        res_data = {}
        res_data['error'] = error_obj.message

        res_data_json = self._encodeData(res_data, accept)

        return HttpResponse(res_data_json, status=error_obj.status_code, content_type='application/json') 

    def success(self, res_data, accept):
        res_data_json = self._encodeData(res_data, accept)

        return HttpResponse(res_data_json, content_type='application/json') 

    def _encodeData(self, res_data, accept):
        if accept == 'application/json':
            return self._jsonEncode(res_data)

        else:
            return self._jsonEncode(res_data)

    def _jsonEncode(self, res_data): 
        try:
            res_json = json.dumps(res_data , sort_keys=True)            
            return res_json

        except Exception as e:
            self.logger.error('JSON Encode Error: %s' %(e))
            return ''
