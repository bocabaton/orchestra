#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import httplib
import urllib
import json  
from dicttoxml import dicttoxml
import xmltodict

class RestClient():

    CONTENT_TYPE = {
        "json": "application/json", 
        "xml": "application/xml", 
        "post": "application/x-www-form-urlencoded"
    }

    ACCEPT = {
        "json": "application/json", 
        "xml": "application/xml",
        "text": "text/plain"
    }

    def __init__(self, ip, **kwargs): 
        # Default Server Settings
        self.options = {}
        self.ip = ip
        self.url = kwargs.get('url', '/')
        self.protocol = kwargs.get('protocol', 'http')

        if kwargs.has_key('port'):
            self.port = int(kwargs['port'])
        else:
            if self.protocol == 'https':
                self.port = 443
            else:
                self.port = 80

        # Default XML Root : root
        self.xml_root = kwargs.get('xml_root', 'root')

        # Default Content Type & Accept: json
        self.headers = {}

        self.content_type = kwargs.get('content_type', 'json')
        self.headers['Content-type'] = self.CONTENT_TYPE[self.content_type]

        self.accept = kwargs.get('accept', 'json')
        self.headers['Accept'] = self.ACCEPT[self.accept]

        # Auth Token Settings
        if kwargs.has_key('token'):
            self.headers['Authorization'] = 'Token %s' %(str(kwargs['token']))

        if kwargs.has_key('xtoken'):
            self.headers['X-Auth-Token'] = '%s' %(str(kwargs['xtoken']))

    def update(self, **kwargs):
        if kwargs.has_key('ip'):
            self.ip = kwargs['ip']

        if kwargs.has_key('url'):
            self.url = kwargs['url']

        if kwargs.has_key('protocol'):
            self.protocol = kwargs['protocol']

        if kwargs.has_key('port'):
            self.port = int(kwargs['port'])

        if kwargs.has_key('xml_root'):
            self.xml_root = kwargs['xml_root']

        if kwargs.has_key('content_type'):
            self.content_type = kwargs['content_type']
            self.headers['Content-type'] = self.CONTENT_TYPE[self.content_type]

        if kwargs.has_key('accept'):
            self.accept = kwargs['accept']
            self.headers['Accept'] = self.ACCEPT[self.accept]

        if kwargs.has_key('token'):
            self.headers['Authorization'] = 'Token %s' %(str(kwargs['token']))

        if kwargs.has_key('xtoken'):
            self.headers['X-Auth-Token'] = '%s' %(str(kwargs['xtoken']))

    def request(self, method='GET', **kwargs):
        (url, params) = self._parseRequest(**kwargs)

        try:
            if method in ['POST', 'PUT']:
                encoded_params = self._encodeParams(params)
            else:
                encoded_params = self._urlEncode(params)

            if self.protocol == 'https':
                conn = httplib.HTTPSConnection(self.ip, self.port)
            else:
                conn = httplib.HTTPConnection(self.ip, self.port)

            if method in ['POST', 'PUT']:
                conn.request(method, url, encoded_params, self.headers)
            else:
                conn.request(method, '%s?%s' %(url, encoded_params), '', self.headers)

            res = conn.getresponse()
            content_type = self._getContentType(res.getheaders())
            received_data = res.read()

            decoded_data = self._decodeData(received_data, content_type)

            return (res.status, decoded_data)

        except Exception as e:
            print e
            return False, e

    def _getContentType(self, header_list):
        for item in header_list:
            if item[0].upper() == 'CONTENT-TYPE':
                return item[1].split(';')

        return "text/plain"

    def _parseRequest(self, **kwargs):
        if kwargs.has_key('url'):
            url = kwargs['url']
        else:
            url = self.url

        if kwargs.has_key('params'):
            params = kwargs['params']
        else:
            params = {}

        return (url, params)

    def _encodeParams(self, params):
        if self.content_type == "json":
            encoded_params = self._jsonEncode(params)
        elif self.content_type == "xml":
            encoded_params = self._xmlEncode(params)
        else:
            encoded_params = self._urlEncode(params)

        return encoded_params

    def _decodeData(self, data, content_type):
        if "application/json" in content_type:
            decoded_data = self._jsonDecode(data)
        elif "application/xml" in content_type:
            decoded_data = self._xmlDecode(data)
        else:
            decoded_data = data

        return decoded_data

    def _urlEncode(self, req_params):
        params = urllib.urlencode(req_params)
        return params

    def _xmlEncode(self, req_params): 
        try:
            req_xml = dicttoxml(req_params, attr_type=False, custom_root=self.xml_root) 
            return req_xml

        except Exception as e:
            print e
            return False
            
    def _xmlDecode(self, res_xml): 
        try:
            res_params = xmltodict.parse(res_xml.strip())
            return res_params

        except Exception as e:
            print e
            return False

    def _jsonEncode(self, req_params): 
        try:
            req_json = json.dumps(req_params , sort_keys=True)            
            return req_json

        except Exception as e:
            print e
            return False

    def _jsonDecode(self, res_json):
        try:
            res_params = json.loads(res_json)
            return res_params

        except Exception as e:
            print e
            return False

if __name__ == "__main__":
    pass
