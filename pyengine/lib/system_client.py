import traceback, logging
from pyengine.lib.restclient import RestClient

class SystemClient:

    logger = logging.getLogger(__name__)

    def __init__(self, host, **kwargs):
        self.conn = RestClient(host, **kwargs)

    def request(self, method, url, params={}):
        response = {}

        try:
            (status, result) = self.conn.request(method, url=url, params=params)

            if status == 200:
                response['status'] = True
                response['response'] = result

            else:
                response['status'] = False
                response['message'] = result['error']['message']

        except Exception as e:
            self.logger.error('Connection failed : %s' %e)
            response['status'] = False
            response['message'] = 'Connection failed.' 

        return response
