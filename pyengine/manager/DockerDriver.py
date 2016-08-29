import requests
import random
import json
import docker
import time

from docker import Client

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class DockerDriver(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def discover(self, param, ctx):
        """
        NOT implemented
        """
        # return Zones
        return ([], 0)


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

        docker_info = cloudMgr._getZoneDetail(zone_id)
        self.logger.debug(docker_info)
        base_url = docker_info['DOCKER_HOST']
        # 2. Create docker client
        client = Client(base_url=base_url)

        # 3. Create Server
        # Add placement based on zone_name
        self.logger.debug(req)

        # Pull Image first
        pulled = client.pull(req['image'], stream=True)
        self.logger.debug("Pulled Imaged:%s" % pulled)

        container = client.create_container(**req)
        response = client.start(container=container.get('Id'))
        self.logger.debug(response)

        inspect = client.inspect_container(container.get('Id'))
        self.logger.debug(inspect)
      
        server = {}
        server['server_id'] = inspect['Id']
        server['private_ip_address'] = inspect['NetworkSettings']['IPAddress']
        self.logger.debug("Create Server => private IP:%s" % server['private_ip_address'])
        server['floating_ip'] = inspect['Node']['IP']
        # (TODO) This may be private IP
        # If it is related with Docker Swarm cluster 
        # Find floating IP address of node
        server['status'] = inspect['State']['Status']

        # CPU, Memory, Disk
        # based on instance_type, get cpu, memory, disk size manaually
        # notice: There are no API for get CPU, Memory, Disk

        return server

#    def updateName(self, auth, zone_id, server_id, name):
#        # 1. Get Endpoint of Zone
#        cloudMgr = self.locator.getManager('CloudManager')
#        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
#
#        s_info = cloudMgr.getServerInfo(server_id)
#        #Assume server_id is always existing
#        cloud_id = s_info['server_id']
#
#        auth_data = auth['auth']
#        a_key = auth_data['access_key_id']
#        sa_key = auth_data['secret_access_key']
#
#        # 2. Create EC2 session
#        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
#        ec2 = session.resource('ec2')
#        ec2.create_tags(Resources = [cloud_id], Tags = [{'Key':'Name','Value':name}])
#
#        
#    def discoverServer(self, auth, zone_id, req):
#        """
#         @param : auth
#            {"auth":{
#               "access_key_id":"ACCESS Key ID",
#               "secret_access_key":"Secret Access Key",
#                }
#            }
#        @param: zone_id
#        @param: req (Dic)
#            {"server_id":"xxx-xxxx-xxx"}
#            {"name":"server_name"}
#        """
#        # 1. Get Endpoint of Zone
#        cloudMgr = self.locator.getManager('CloudManager')
#        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
#
#        auth_data = auth['auth']
#        a_key = auth_data['access_key_id']
#        sa_key = auth_data['secret_access_key']
#
#        # 2. Create EC2 session
#        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
#        ec2 = session.resource('ec2')
#
#        #TODO
#    def discoverServers(self, auth, zone_id):
#        """
#        find all servers at zone
#        @return: list of server info
#        """
#        # 1. Get Endpoint of Zone
#        cloudMgr = self.locator.getManager('CloudManager')
#        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
#
#        auth_data = auth['auth']
#        a_key = auth_data['access_key_id']
#        sa_key = auth_data['secret_access_key']
#
#        # 2. Create EC2 session
#        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
#        ec2 = session.resource('ec2')
#
#        machines = ec2.instances.filter(Filters=[{'Name':'availability-zone','Values':[z_name]}])
#        output = []
#        for machine in machines:
#            dic = {}
#            dic['name'] = ''
#            if machine.tags:
#                for tag in machine.tags:
#                    if tag['Key'] == 'Name':
#                        dic['name'] = tag['Value']
#                        break
#            dic['server_id'] = machine.instance_id
#            dic['private_ip_address'] = machine.private_ip_address
#            dic['floating_ip'] = machine.public_ip_address
#            dic['status'] = machine.state['Name']
#            # Register Machine
#            output.append(dic)
#
#        return output
#
#    def stopServer(self, auth, zone_id, req):
#        """
#         @param : auth
#            {"auth":{
#               "key_id":"Key ID",
#               "secret":"Secret Key",
#                }
#            }
#        @param: zone_id
#        @param: req (Dic)
#            {"server_id":"xxx-xxxx-xxx"}
#        """
#        # 1. Get Endpoint of Zone
#        cloudMgr = self.locator.getManager('CloudManager')
#        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
#
#        auth_data = auth['auth']
#        a_key = auth_data['access_key_id']
#        sa_key = auth_data['secret_access_key']
#
#        # 2. Create EC2 session
#        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
#        ec2 = session.resource('ec2')
#
#        if req.has_key('server_id') == True:
#            mid = req['server_id']
#            machines = ec2.instances.filter(InstanceIds=[mid]).stop()
#            for machine in machines:
#                dic = {}
#                dic['status'] = machine.state['Name']
#                return dic
#        # This is error
#        return {}
#
#    def deleteServer(self, auth, zone_id, req):
#        """
#         @param : auth
#            {"auth":{
#               "key_id":"Key ID",
#               "secret":"Secret Key",
#                }
#            }
#        @param: zone_id
#        @param: req (Dic)
#            {"server_id":"xxx-xxxx-xxx"}
#        """
#        # 1. Get Endpoint of Zone
#        cloudMgr = self.locator.getManager('CloudManager')
#        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
#
#        auth_data = auth['auth']
#        a_key = auth_data['access_key_id']
#        sa_key = auth_data['secret_access_key']
#
#        # 2. Create EC2 session
#        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
#        ec2 = session.resource('ec2')
#
#        if req.has_key('server_id'):
#            mid = req['server_id']
#            machines = ec2.instances.filter(InstanceIds=[mid]).terminate()
#            for machine in machines:
#                dic = {}
#                dic['status'] = machine.state['Name']
#                return dic
#        # This is error
#        return {}
#
#
#    def getServerStatus(self, auth, zone_id, server_id):
#        """
#        @param : 
#            - auth : user info for aws
#            {"auth":{
#                   "access_key_id":"choonho.son",
#                   "secret_access_key":"choonho.son",
#                }
#            }
#
#            - server_id: EC2 instance_id
#
#        """
#        # 1. Get Endpoint of Zone
#        cloudMgr = self.locator.getManager('CloudManager')
#        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
#
#        auth_data = auth['auth']
#        a_key = auth_data['access_key_id']
#        sa_key = auth_data['secret_access_key']
#
#        # 2. Create ec2 session
#        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
#        ec2 = session.resource('ec2')
#        # 3. Create Server
# 
#
#        # 3. Get Show server details
#        instances = ec2.instances.filter(Filters=[{'Name':'instance-id','Values':[server_id]}])
#        i_json = {}
#        for instance in instances:
#            i_json = {
#                "ami_launch_index": instance.ami_launch_index,
#                "architecture": instance.architecture,
#                "client_token": instance.client_token,
#                "ebs_optimized": instance.ebs_optimized,
#                "hypervisor": instance.hypervisor,
#                "iam_instance_profile": instance.iam_instance_profile,
#                "image_id": instance.image_id,
#                "instance_id": instance.instance_id,
#                "instance_lifecycle": instance.instance_lifecycle,
#                "instance_type": instance.instance_type,
#                "kernel_id": instance.kernel_id,
#                "key_name": instance.key_name,
#                "launch_time": str(instance.launch_time),
#                "monitoring": instance.monitoring,
#                "placement": instance.placement,
#                "platform": instance.platform,
#                "private_dns_name": instance.private_dns_name,
#                "private_ip_address": instance.private_ip_address,
#                "product_codes": instance.product_codes,
#                "public_dns_name": instance.public_dns_name,
#                "public_ip_address": instance.public_ip_address,
#                "ramdisk_id": instance.ramdisk_id,
#                "root_device_name": instance.root_device_name,
#                "root_device_type": instance.root_device_type,
#                "security_groups": instance.security_groups,
#                "source_dest_check": instance.source_dest_check,
#                "spot_instance_request_id": instance.spot_instance_request_id,
#                "sriov_net_support": instance.sriov_net_support,
#                "state": instance.state,
#                "state_reason": instance.state_reason,
#                "state_transition_reason": instance.state_transition_reason,
#                "subnet_id": instance.subnet_id,
#                "tags": instance.tags,
#                "virtualization_type": instance.virtualization_type,
#                "vpc_id": instance.vpc_id,
#            }
#            self.logger.debug("Get Server Status => private IP:%s" % i_json['private_ip_address'])
#            return {'status': i_json['state']['Name'], 'private_ip_address':i_json['private_ip_address']}  
#        return {'status':'unknown'}
#
#    def addFloatingIP(self, auth, zone_id, server_id):
#        """
#        @param : 
#            - auth : user info for aws
#            {"auth":{
#                   "access_key_id":"choonho.son",
#                   "secret_access_key":"choonho.son",
#                }
#            }
#
#            - server_id: EC2 instance_id
#
#        """
#        # 1. Get Endpoint of Zone
#        cloudMgr = self.locator.getManager('CloudManager')
#        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)
#
#        auth_data = auth['auth']
#        a_key = auth_data['access_key_id']
#        sa_key = auth_data['secret_access_key']
#
#        # 2. Create ec2 session
#        session = Session(aws_access_key_id=a_key, aws_secret_access_key=sa_key, region_name=r_name)
#        ec2 = session.resource('ec2')
#
#        # 3. Get Show server details
#        for i in range(50):
#            instances = ec2.instances.filter(Filters=[{'Name':'instance-id','Values':[server_id]}])
#            self.logger.debug("[count: %d] get server detail" % i)
#            i_json = {}
#            for instance in instances:
#                i_json = {
#                    "ami_launch_index": instance.ami_launch_index,
#                    "architecture": instance.architecture,
#                    "client_token": instance.client_token,
#                    "ebs_optimized": instance.ebs_optimized,
#                    "hypervisor": instance.hypervisor,
#                    "iam_instance_profile": instance.iam_instance_profile,
#                    "image_id": instance.image_id,
#                    "instance_id": instance.instance_id,
#                    "instance_lifecycle": instance.instance_lifecycle,
#                    "instance_type": instance.instance_type,
#                    "kernel_id": instance.kernel_id,
#                    "key_name": instance.key_name,
#                    "launch_time": str(instance.launch_time),
#                    "monitoring": instance.monitoring,
#                    "placement": instance.placement,
#                    "platform": instance.platform,
#                    "private_dns_name": instance.private_dns_name,
#                    "private_ip_address": instance.private_ip_address,
#                    "product_codes": instance.product_codes,
#                    "public_dns_name": instance.public_dns_name,
#                    "public_ip_address": instance.public_ip_address,
#                    "ramdisk_id": instance.ramdisk_id,
#                    "root_device_name": instance.root_device_name,
#                    "root_device_type": instance.root_device_type,
#                    "security_groups": instance.security_groups,
#                    "source_dest_check": instance.source_dest_check,
#                    "spot_instance_request_id": instance.spot_instance_request_id,
#                    "sriov_net_support": instance.sriov_net_support,
#                    "state": instance.state,
#                    "state_reason": instance.state_reason,
#                    "state_transition_reason": instance.state_transition_reason,
#                    "subnet_id": instance.subnet_id,
#                    "tags": instance.tags,
#                    "virtualization_type": instance.virtualization_type,
#                    "vpc_id": instance.vpc_id,
#                }
#                if i_json['public_ip_address'] != None:
#                    return i_json['public_ip_address']
#
#            self.logger.info("Instance is not ready")
#            time.sleep(10)
