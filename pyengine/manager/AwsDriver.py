import requests
import random
import json
import boto3
import time

from boto3.session import Session

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class AwsDriver(Manager):

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
        """
        # 1. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)

        auth_data = auth['auth']
        a_key = auth_data['access_key_id']
        sa_key = auth_data['secret_access_key']

        # 2. Create ec2 session
        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
        ec2 = session.resource('ec2')
        # 3. Create Server
        
        #instances = globals()['ec2.create_instances'](**req)
        instances = ec2.create_instances(**req)
        # We support only one instance
        instance = instances[0]
        instance_info = {
            "ami_launch_index": instance.ami_launch_index,
            "architecture": instance.architecture,
            "client_token": instance.client_token,
            "ebs_optimized": instance.ebs_optimized,
            "hypervisor": instance.hypervisor,
            "iam_instance_profile": instance.iam_instance_profile,
            "image_id": instance.image_id,
            "instance_id": instance.instance_id,
            "instance_lifecycle": instance.instance_lifecycle,
            "instance_type": instance.instance_type,
            "kernel_id": instance.kernel_id,
            "key_name": instance.key_name,
            "launch_time": str(instance.launch_time),
            "monitoring": instance.monitoring,
            "placement": instance.placement,
            "platform": instance.platform,
            "private_dns_name": instance.private_dns_name,
            "private_ip_address": instance.private_ip_address,
            "product_codes": instance.product_codes,
            "public_dns_name": instance.public_dns_name,
            "public_ip_address": instance.public_ip_address,
            "ramdisk_id": instance.ramdisk_id,
            "root_device_name": instance.root_device_name,
            "root_device_type": instance.root_device_type,
            "security_groups": instance.security_groups,
            "source_dest_check": instance.source_dest_check,
            "spot_instance_request_id": instance.spot_instance_request_id,
            "sriov_net_support": instance.sriov_net_support,
            "state": instance.state,
            "state_reason": instance.state_reason,
            "state_transition_reason": instance.state_transition_reason,
            "subnet_id": instance.subnet_id,
            "tags": instance.tags,
            "virtualization_type": instance.virtualization_type,
            "vpc_id": instance.vpc_id,
        }
        server = {}
        server['server_id'] = instance_info['instance_id']
        #server['private_ip_address'] = instance_info['private_ip_address']
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

        auth_data = auth['auth']
        a_key = auth_data['access_key_id']
        sa_key = auth_data['secret_access_key']

        # 2. Create ec2 session
        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
        ec2 = session.resource('ec2')
        # 3. Create Server
 

        # 3. Get Show server details
        instances = ec2.instances.filter(Filters=[{'Name':'instance-id','Values':[server_id]}])
        i_json = {}
        for instance in instances:
            i_json = {
                "ami_launch_index": instance.ami_launch_index,
                "architecture": instance.architecture,
                "client_token": instance.client_token,
                "ebs_optimized": instance.ebs_optimized,
                "hypervisor": instance.hypervisor,
                "iam_instance_profile": instance.iam_instance_profile,
                "image_id": instance.image_id,
                "instance_id": instance.instance_id,
                "instance_lifecycle": instance.instance_lifecycle,
                "instance_type": instance.instance_type,
                "kernel_id": instance.kernel_id,
                "key_name": instance.key_name,
                "launch_time": str(instance.launch_time),
                "monitoring": instance.monitoring,
                "placement": instance.placement,
                "platform": instance.platform,
                "private_dns_name": instance.private_dns_name,
                "private_ip_address": instance.private_ip_address,
                "product_codes": instance.product_codes,
                "public_dns_name": instance.public_dns_name,
                "public_ip_address": instance.public_ip_address,
                "ramdisk_id": instance.ramdisk_id,
                "root_device_name": instance.root_device_name,
                "root_device_type": instance.root_device_type,
                "security_groups": instance.security_groups,
                "source_dest_check": instance.source_dest_check,
                "spot_instance_request_id": instance.spot_instance_request_id,
                "sriov_net_support": instance.sriov_net_support,
                "state": instance.state,
                "state_reason": instance.state_reason,
                "state_transition_reason": instance.state_transition_reason,
                "subnet_id": instance.subnet_id,
                "tags": instance.tags,
                "virtualization_type": instance.virtualization_type,
                "vpc_id": instance.vpc_id,
            }
            return {'status': i_json['state']['Name'], 'private_ip_address':i_json['private_ip_address']}  
        return {'status':'unknown'}

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
        # 1. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)

        auth_data = auth['auth']
        a_key = auth_data['access_key_id']
        sa_key = auth_data['secret_access_key']

        # 2. Create ec2 session
        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
        ec2 = session.resource('ec2')

        # 3. Get Show server details
        for i in range(10):
            instances = ec2.instances.filter(Filters=[{'Name':'instance-id','Values':[server_id]}])
            i_json = {}
            for instance in instances:
                i_json = {
                    "ami_launch_index": instance.ami_launch_index,
                    "architecture": instance.architecture,
                    "client_token": instance.client_token,
                    "ebs_optimized": instance.ebs_optimized,
                    "hypervisor": instance.hypervisor,
                    "iam_instance_profile": instance.iam_instance_profile,
                    "image_id": instance.image_id,
                    "instance_id": instance.instance_id,
                    "instance_lifecycle": instance.instance_lifecycle,
                    "instance_type": instance.instance_type,
                    "kernel_id": instance.kernel_id,
                    "key_name": instance.key_name,
                    "launch_time": str(instance.launch_time),
                    "monitoring": instance.monitoring,
                    "placement": instance.placement,
                    "platform": instance.platform,
                    "private_dns_name": instance.private_dns_name,
                    "private_ip_address": instance.private_ip_address,
                    "product_codes": instance.product_codes,
                    "public_dns_name": instance.public_dns_name,
                    "public_ip_address": instance.public_ip_address,
                    "ramdisk_id": instance.ramdisk_id,
                    "root_device_name": instance.root_device_name,
                    "root_device_type": instance.root_device_type,
                    "security_groups": instance.security_groups,
                    "source_dest_check": instance.source_dest_check,
                    "spot_instance_request_id": instance.spot_instance_request_id,
                    "sriov_net_support": instance.sriov_net_support,
                    "state": instance.state,
                    "state_reason": instance.state_reason,
                    "state_transition_reason": instance.state_transition_reason,
                    "subnet_id": instance.subnet_id,
                    "tags": instance.tags,
                    "virtualization_type": instance.virtualization_type,
                    "vpc_id": instance.vpc_id,
                }
                if i_json['public_ip_address'] != None:
                    return i_json['public_ip_address']

            self.logger.info("Instance is not ready")
            time.sleep(5)
