import requests
import random
import json
import time

from boto3.session import Session

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class BaremetalDriver(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def discover(self, param):
        """
        @param: 
            "auth":{
               "access_key_id":"ACCESS Key ID",
               "secret_access_key":"Secret Access Key",
               "region_name":"your prefered region name",
               }
            }
        """
        auth = param['auth']
        if auth.has_key('access_key_id') == False:
            raise ERROR_AUTH_FAILED(reason="Access Key ID is needed")
        else:
            a_key = auth['access_key_id']
        if auth.has_key('secret_access_key') == False:
            raise ERROR_AUTH_FAILED(reason="Secret Access Key is needed")
        else:
            sa_key = auth['secret_access_key']
        if auth.has_key('region_name') == False:
            self.logger.info("Use default region_name:us-east-1")
            r_name = 'us-east-1'
        else:
            r_name = auth['region_name']
        client = boto3.client('ec2',region_name=r_name, aws_access_key_id=a_key, aws_secret_access_key=sa_key)
        
        # base on endpoint, Create Region
        cloudMgr = self.locator.getManager('CloudManager')
        # 1. Create Region
        regions = self._getRegions(client.describe_regions())

        output = []
        total_count = 0
        for region in regions:
            param = {'name':region}
            region_info = cloudMgr.createRegion(param)
            total_count = total_count + 1
            output.append(region_info)
            # 2. Detect Availability Zones
            az_list = self.getAvailabilityZones(a_key, sa_key, region)
            for az in az_list:
                param = {'name': az, 
                         'region_id': region_info.output['region_id'],
                         'zone_type': 'aws'}
                zone_info = cloudMgr.createZone(param)

        # return Zones
        return (output, total_count)


    def _getRegions(self, region_info):
        """
        @param: value of 'ec2.describe_regions()'
            {'Regions': [{'Endpoint': 'ec2.eu-west-1.amazonaws.com',
              'RegionName': 'eu-west-1'},
             {'Endpoint': 'ec2.ap-southeast-1.amazonaws.com',
              'RegionName': 'ap-southeast-1'},
             {'Endpoint': 'ec2.ap-southeast-2.amazonaws.com',
              'RegionName': 'ap-southeast-2'},
             {'Endpoint': 'ec2.eu-central-1.amazonaws.com',
              'RegionName': 'eu-central-1'},
             {'Endpoint': 'ec2.ap-northeast-2.amazonaws.com',
              'RegionName': 'ap-northeast-2'},
             {'Endpoint': 'ec2.ap-northeast-1.amazonaws.com',
              'RegionName': 'ap-northeast-1'},
             {'Endpoint': 'ec2.us-east-1.amazonaws.com',
              'RegionName': 'us-east-1'},
             {'Endpoint': 'ec2.sa-east-1.amazonaws.com',
              'RegionName': 'sa-east-1'},
             {'Endpoint': 'ec2.us-west-1.amazonaws.com',
              'RegionName': 'us-west-1'},
             {'Endpoint': 'ec2.us-west-2.amazonaws.com',
              'RegionName': 'us-west-2'}],
             'ResponseMetadata': {'HTTPStatusCode': 200,
                          'RequestId': '123456789-1234-1234-1234-123456789'}}
       """
        region = set()
        for item in region_info['Regions']:
            if item.has_key('RegionName'):
                region.add(item['RegionName'])
        return region

    def getAvailabilityZones(self, a_key, sa_key, r_name):
        """
        @params:
            - a_key: access key id
            - sa_key : secret access key
            - region_name: Region name (ex. us-east-1)
        """
        self.logger.debug("Discover Zone at %s" % r_name)
        client = boto3.client('ec2',region_name=r_name, aws_access_key_id=a_key, aws_secret_access_key=sa_key)
        az_infos = client.describe_availability_zones(DryRun=False, Filters=[{'Name':'region-name','Values':[r_name]}])
        """
        {u'AvailabilityZones': 
            [{u'State': 'available', u'RegionName': 'us-west-2', u'Messages': [], u'ZoneName': 'us-west-2a'}, 
            {u'State': 'available', u'RegionName': 'us-west-2', u'Messages': [], u'ZoneName': 'us-west-2b'}, 
            {u'State': 'available', u'RegionName': 'us-west-2', u'Messages': [], u'ZoneName': 'us-west-2c'}], 
            'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': 'e4e83d6c-022f-443f-ba58-eb81e49bda27'}}
        """
        output = []
        for az_info in az_infos['AvailabilityZones']:
            if az_info['State'] == 'available':
                output.append(az_info['ZoneName'])

        return output


    ###############################################
    # Deploy
    ###############################################
    def deployServer(self, auth, zone_id, req):
        """
        @param : auth
            {"auth":{
               "access_key_id":"ACCESS Key ID",
               "secret_access_key":"Secret Access Key",
                }
            }
        @param: zone_id
        @param: req (Dic)
            {
            "private_ip_address":"10.1.1.1",
            "ipmi_ip_address":"10.1.1.101",
            "ipmi_account":"root",
            "ipmi_password":"ipmi_password"
            ...
            }
        """
        # 1. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
        
        # 3. Create Server
        #   For bare-metal, we just register server information 
        #       which is passed by req parameter
        # TODO: check the server information is correct?

        server = {}
        # TODO: what is server_id?
        import uuid
        server['server_id'] = uuid.uuid4()
        server['private_ip_address'] = req['private_ip_address']
        return server

    def getServerStatus(self, auth, zone_id, server_id):
        """
        @param : 
            - auth : user info for aws
            {"auth":{
                   "access_key_id":"choonho.son",
                   "secret_access_key":"choonho.son",
                }
            }

            - server_id: EC2 instance_id

        """
        # 1. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)

        # 2. Check Server Status
        body = {'server_id':server_id, 'cmd':'hostname'}
        
        # 3. Get Show server details
        return {'status':'ACTIVE'}

    def addFloatingIP(self, auth, zone_id, server_id):
        """
        @param : 
            - auth : user info for aws
            {"auth":{
                   "access_key_id":"choonho.son",
                   "secret_access_key":"choonho.son",
                }
            }

            - server_id: EC2 instance_id

        """
        pass
