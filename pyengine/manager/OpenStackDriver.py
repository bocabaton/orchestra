import requests
import random
import json

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class OpenStackDriver(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def discover(self, param):
        """
        @param: 
            "keystone":"http://10.1.0.1:5000/v2.0",
            "auth":{
               "tenantName":"choonho.son",
               "passwordCredentials":{
                  "username": "choonho.son",
                  "password": "123456"
               }
            }
        """
        access = self.getAccess(param['keystone'], {'auth':param['auth']})
        
        # Parse serviceCatalog
        catalog = access['serviceCatalog']
        token   = access['token']

        # base on endpoint, Create Region
        cloudMgr = self.locator.getManager('CloudManager')
        # 1. Create Region
        regions = self._getRegions(catalog)
        tenantId = self._getTenantId(token)
        tokenId = self._getTokenId(token)

        output = []
        total_count = 0
        for region in regions:
            param = {'name':region}
            region_info = cloudMgr.createRegion(param)
            total_count = total_count + 1
            output.append(region_info)
            # 2. Detect Availability Zones
            endpoint = self._getEndpoint(catalog, region)
            az_list = self.getAvailabilityZones(tokenId, endpoint, tenantId)
            for az in az_list:
                param = {'name': az, 
                         'region_id': region_info.output['region_id'],
                         'zone_type': 'openstack'}
                zone_info = cloudMgr.createZone(param)

        # return Zones
        return (output, total_count)


    def _getRegions(self, catalog):
        """
        @param: value of 'serviceCatalog'
            [ { u'endpoints': [ { u'adminURL': u'http://10.1.0.1:8774/v2/9063caa05aab41cd8e34ef6a115e0915',
                                  u'id': u'7862b9253c364fd989b137c860db8e9a',
                                  u'internalURL': u'http://10.1.0.1:8774/v2/9063caa05aab41cd8e34ef6a115e0915',
                                  u'publicURL': u'http://10.1.0.1:8774/v2/9063caa05aab41cd8e34ef6a115e0915',
                                  u'region': u'RegionOne'}],
               u'endpoints_links': [],
               u'name': u'nova',
               u'type': u'compute'},
            
              { u'endpoints': [ { u'adminURL': u'http://10.1.0.1:9696',
                                  u'id': u'83381d4f04cb443290b886c06c2f71a5',
                                  u'internalURL': u'http://10.1.0.1:9696',
                                  u'publicURL': u'http://10.1.0.1:9696',
                                  u'region': u'RegionOne'}],
                                  u'endpoints_links': [],
                                  u'name': u'neutron',
                                  u'type': u'network'},
        """
        region = set()
        for item in catalog:
            if item.has_key('type'):
                if item['type'] == 'compute':
                    for endpoint in item['endpoints']:
                        region.add(endpoint['region'])
        return region

    def _getEndpoint(self, catalog, region, svc_type='compute', url_type='publicURL'):
        """
        return the endpoint of specific regions and type
        @param: value of 'serviceCatalog'
 
        """
        for item in catalog:
            if item['type'] == svc_type:
                for endpoint in item['endpoints']:
                    if endpoint['region'] == region:
                        return endpoint[url_type]
        return None

    def _getTenantId(self, token):
        """
        @param: access['token']
        @return: tenant ID
        """
        return token['tenant']['id']

    def _getTokenId(self, token):
        """
        @param: access['token']
        @return: Token ID
        """
        return token['id']


    def getAccess(self, keystone, auth):
        """
        @keystone:
            http://192.168.1.1:5000/v2.0
        @auth:
            {"auth":{
                "tenantName":"choonho.son",
                "passwordCredentials":{
                    "username":"choonho.son",
                    "password":"123456"
                }
            }

        @return: access
        """

        # make get token request
        hdr = {'Content-Type':'application/json'}
        r_data = auth
        url = "%s/tokens" % keystone
        self.logger.debug("Req URL:%s" % url)
        r = requests.post(url, headers=hdr, data=json.dumps(r_data))
        
        self.logger.debug("Output:%s" % r.text)
        if r.status_code == 200 or r.status_code == 203:
            result = json.loads(r.text)
            return result['access']
        # Error
        elif r.status_code == 403:
            raise ERROR_AUTH_FAILED(reason="userDisabled")
        elif r.status_code == 400:
            raise ERROR_AUTH_FAILED(reason="Bad Request")
        elif r.status_code == 401:
            raise ERROR_AUTH_FAILED(reason="Unauthorized")
        elif r.status_code == 403:
            raise ERROR_AUTH_FAILED(reason="Forbidden")
        elif r.status_code == 404:
            raise ERROR_AUTH_FAILED(reason="Not Found")
        elif r.status_code == 405:
            raise ERROR_AUTH_FAILED(reason="Method Not Allowed")
        elif r.status_code == 413:
            raise ERROR_AUTH_FAILED(reason="Request Entity Too Large")
        elif r.status_code == 503:
            raise ERROR_AUTH_FAILED(reason="Service Unavailable")
        else:
            raise ERROR_AUTH_FAILED(reason="Unknown") 

    def getAvailabilityZones(self, token, endpoint, tenant_id):
        """
        url: /v2.1/{tenant_id}/os-availability-zone
        method: GET

        response
            {
                "availabilityZoneInfo": [
                    {
                        "zoneState": {
                            "available": true
                        },
                        "hosts": null,
                        "zoneName": "nova"
                    }
                ]
            }
        @return: list of availability zone
        ex) ['nova']

        """
        hdr = {'Content-Type':'application/json','X-Auth-Token':token}
        url = "%s/os-availability-zone" % endpoint
        r = requests.get(url, headers = hdr)

        output = []
        if r.status_code == 200:
            result = json.loads(r.text)
            self.logger.debug("Show availability zone =>\n %s" % r.text)
            az_infos = result['availabilityZoneInfo']
            for az in az_infos:
                # TODO: check state
                output.append(az['zoneName'])
            return output

        # TODO: Error check
        raise ERROR_OPENSTACK(reason=url)


    ###############################################
    # Deploy
    ###############################################
    def deployServer(self, auth, zone_id, req):
        """
        @param : auth
            {"auth":{
                   "tenantName":"choonho.son",
                   "passwordCredentials":{
                      "username": "choonho.son",
                      "password": "123456"
                   }
                }
            }
        @param: zone_id
        @param: req
        """

        # 1. Get Token 
        #    . find keystone url from zone_detail
        #    
        keystone = 'http://10.1.0.1:5000/v2.0'
        access = self.getAccess(keystone, auth)
        token_id = self._getTokenId(access['token'])
        
        # 2. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
        endpoint = self._getEndpoint(access['serviceCatalog'],r_name,'compute','publicURL')

        # 3. Create Server
        hdr = {'Content-Type':'application/json', 'X-Auth-Token':token_id}
        r_data = req
        url = '%s/servers' % endpoint
        r = requests.post(url, headers=hdr, data=json.dumps(r_data))
        if r.status_code == 202:
            result = json.loads(r.text)
            self.logger.debug(r.text)
            server = {}
            # Server ID
            server['server_id'] = result['server']['id']
            # Address
            """
            "addresses": {
              "subnet-choonho.son": [
                {"OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:8a:ba:e5", 
                "version": 4, 
                "addr": "192.168.1.120", 
                "OS-EXT-IPS:type": "fixed"}]
            },
            """
            if result['server'].has_key('addresses'):
                temp = result['server']['addresses']
                for key in temp.keys():
                    v2 = temp[key]
                    for item in v2:
                        addr = item['addr']
                        # TODO: we assume VM has one IP
                        server['private_ip_address'] = addr

            return server
        return {"failed":json.loads(r.text)}

    def addFloatingIP(self, auth, zone_id, server_id):
        """
        @param : 
            - auth : user info for keystone token
            {"auth":{
                   "tenantName":"choonho.son",
                   "passwordCredentials":{
                      "username": "choonho.son",
                      "password": "123456"
                   }
                }
            }

            - server_id: OpenStack server_id

        """

        # 1. Get Token 
        #    . find keystone url from zone_detail
        #    
        keystone = 'http://10.1.0.1:5000/v2.0'
        access = self.getAccess(keystone, auth)
        token_id = self._getTokenId(access['token'])
        
        # 2. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
        endpoint = self._getEndpoint(access['serviceCatalog'],r_name,'compute','publicURL')


        # 3. List Pools
        hdr = {'Content-Type':'application/json', 'X-Auth-Token':token_id}
        url = '%s/os-floating-ip-pools' % endpoint
        r = requests.get(url, headers=hdr)
        pool_list = []
        if r.status_code == 200:
            """
            {
                "floating_ip_pools": [
                    {
                        "name": "pool1"
                    },
                    {
                        "name": "pool2"
                    }
                ]
            }
            """
            result = json.loads(r.text)
            pools =result['floating_ip_pools']
            for pool in pools:
                pool_list.append(pool['name'])

        # TODO: no pool
        # For each pool, find usable floating IP
        FIP_FOUND = False
        for pool in pool_list:
            # list floating IP
            url = '%s/os-floating-ips' % endpoint
            r = requests.get(url, headers=hdr)
            """
            {u'floating_ips': 
                [{u'instance_id': u'b28a2edb-9590-4aa5-87b0-047f00026a0d', u'ip': u'192.168.0.16', u'fixed_ip': u'192.168.1.102', u'id': u'062e476d-d783-4d0b-bcc7-814a31a3c798', u'pool': u'public01'}, 
    {u'instance_id': None, u'ip': u'192.168.0.66', u'fixed_ip': None, u'id': u'0b1d6b74-d0b0-4ea1-bea6-21b623479f15', u'pool': u'public01'},
           """

            if r.status_code == 200:
                result = json.loads(r.text)
                fips = result['floating_ips']
                for fip in fips:
                    if fip['instance_id'] == None:
                        address = fip['ip']
                        FIP_FOUND = True 
                        break;

        selected_pool = random.choice(pool_list)
        
        # 4. Create floating IP address
        if FIP_FOUND == False:
            url = '%s/os-floating-ips' % endpoint
            body = {'pool':selected_pool}
            r = requests.post(url, headers=hdr, data=json.dumps(body))
            if r.status_code == 200:
                """
                {
                    "floating_ip": {
                        "instance_id": null,
                        "ip": "172.24.4.4",
                        "fixed_ip": null,
                        "id": "c9c04158-3ed4-449c-953a-aa21fb47cde7",
                        "pool": "public"
                    }
                }
                """
                result = json.loads(r.text)
                address = result['floating_ip']['ip']

        # 5. Add floating IP
        url = '%s/servers/%s/action' % (endpoint, server_id)
        body = {'addFloatingIp':{'address':address}}
        r = requests.post(url, headers=hdr, data=json.dumps(body))
        if r.status_code == 202:
            pass
        else:
            self.logger.debug(r.text)
            self.logger.debug('url:%s' % url)
            raise ERROR_OPENSTACK(key='addFloatingIp', value=address)

        return address

    def getServerStatus(self, auth, zone_id, server_id):
        """
        @param : 
            - auth : user info for keystone token
            {"auth":{
                   "tenantName":"choonho.son",
                   "passwordCredentials":{
                      "username": "choonho.son",
                      "password": "123456"
                   }
                }
            }

            - server_id: OpenStack server_id

        """

        # 1. Get Token 
        #    . find keystone url from zone_detail
        #    
        keystone = 'http://10.1.0.1:5000/v2.0'
        access = self.getAccess(keystone, auth)
        token_id = self._getTokenId(access['token'])
        
        # 2. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
        endpoint = self._getEndpoint(access['serviceCatalog'],r_name,'compute','publicURL')


        # 3. Get Show server details
        hdr = {'Content-Type':'application/json', 'X-Auth-Token':token_id}
        url = '%s/servers/%s' % (endpoint, server_id)
        r = requests.get(url, headers=hdr)
        if r.status_code == 200:
            result = json.loads(r.text)
            self.logger.debug(r.text)
            # Address
            """
            "addresses": {
              "subnet-choonho.son": [
                {"OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:8a:ba:e5", 
                "version": 4, 
                "addr": "192.168.1.120", 
                "OS-EXT-IPS:type": "fixed"}]
            },
            """
            addr=""
            if result['server'].has_key('addresses'):
                temp = result['server']['addresses']
                for key in temp.keys():
                    v2 = temp[key]
                    for item in v2:
                        addr = item['addr']
                        # TODO: we assume VM has one IP

            return {'status': result['server']['status'], 'private_ip_address':addr}
        else:
            return {'status':'unknown'}
