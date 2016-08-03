import requests
import random
import json
import smartdc
import time

from smartdc import DataCenter

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class JoyentDriver(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def discover(self, param, ctx):
        """
        @param: 
            "auth":{
               "key_id":"ACCESS Key ID",
               "secret":"/root/.ssh/joyent_id_rsa"
               }
            }
        """
        auth = param['auth']
        if auth.has_key('key_id') == False:
            raise ERROR_AUTH_FAILED(reason="Key ID is needed")
        else:
            a_key = auth['key_id']
        if auth.has_key('secret') == False:
            raise ERROR_AUTH_FAILED(reason="Secret(registered id_rsa private key)  is needed")
        else:
            s_key = auth['secret']
        sdc = DataCenter(key_id=a_key, secret=s_key)
        
        # base on endpoint, Create Region
        cloudMgr = self.locator.getManager('CloudManager')

        # 1. Create Region
        regions = self._getRegions(sdc.datacenters())

        output = []
        total_count = 0
        for region in regions:
            param = {'name':region}
            region_info = cloudMgr.createRegion(param)
            total_count = total_count + 1
            output.append(region_info)
            # 2. Detect Availability Zones
            # Joyent has no AZ concept, use az = region	
            az_list = [region]
            for az in az_list:
                param = {'name': az, 
                         'region_id': region_info.output['region_id'],
                         'zone_type': 'joyent'}
                zone_info = cloudMgr.createZone(param)

                # Update Zone Detail for DOCKER_HOST
                zone_id = zone_info.output['zone_id']
                self.logger.debug("Add Zone Detail at %s" % zone_id)
                # NOTICE:
                docker_url = 'tcp://%s.docker.joyent.com:2376' % region
                p2 = {'zone_id': zone_id, 'create':[{'key':'DOCKER_HOST','value':docker_url},
                                                {'key':'DOCKER_TLS_VERIFY','value':'1'}]}
                cloudMgr.createZoneDetail(p2)

                # Discover ALL servers and register them
                servers = self.discoverServers({'auth':auth}, zone_id)
                for server in servers:
                    cloudMgr.registerServerByServerInfo(zone_id, server, ctx)

        # return Zones
        return (output, total_count)


    def _getRegions(self, region_info):
        """
        @param: value of 'sdc.datacenters()'
{u'eu-ams-1': u'https://eu-ams-1.api.joyentcloud.com', u'us-east-1': u'https://us-east-1.api.joyentcloud.com', u'us-east-2': u'https://us-east-2.api.joyentcloud.com', u'us-east-3': u'https://us-east-3.api.joyentcloud.com', u'us-sw-1': u'https://us-sw-1.api.joyentcloud.com', u'us-west-1': u'https://us-west-1.api.joyentcloud.com'}
	"""
        region = set()
        for item in region_info.keys():
        	region.add(item)
        return region

    ###############################################
    # Deploy
    ###############################################
    def deployServer(self, auth, zone_id, req):
        """
        @param : auth
            {"auth":{
               "key_id":"Key ID",
               "secret":"Secret Key",
                }
            }
        @param: zone_id
        @param: req (Dic)
            {"name":"test-machine",
            "package":"g4-general-4G",
            "image":'a601aa10-100a-11e6-9eb1-2bbb19e1e3e6',
            ...
        """
        # 1. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)

        auth_data = auth['auth']
        a_key = auth_data['key_id']
        s_key = auth_data['secret']

        # 2. Create DataCenter object
        sdc = DataCenter(location=z_name, key_id=a_key, secret=s_key)
        # 3. Create Server
        self.logger.debug(req)
        instance = sdc.create_machine(**req)
        instance.poll_until('running')

        server = {}
        server['status'] = instance.status()
        server['server_id'] = instance.id
        server['private_ip_address'] = instance.private_ips[0]
        self.logger.debug("Create Server => Private IP:%s" % instance.private_ips[0])
        server['floating_ip'] = instance.public_ips[0]
        self.logger.debug("Create Server => Public IP:%s" % instance.public_ips[0])

        # CPU, Memory, Disk
        if req.has_key('package'):
            packages = sdc.packages(req['package'])
            if len(packages) == 1:
                package = packages[0]
                server['cpus'] = package['vcpus']
                server['memory'] = package['memory']
                server['disk'] = package['disk']

        self.logger.debug("status:%s" % instance.status())

        return server

    def discoverServer(self, auth, zone_id, req):
        """
         @param : auth
            {"auth":{
               "key_id":"Key ID",
               "secret":"Secret Key",
                }
            }
        @param: zone_id
        @param: req (Dic)
            {"server_id":"xxx-xxxx-xxx"}
            {"name":"server_name"}
        """
        # 1. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)

        auth_data = auth['auth']
        a_key = auth_data['key_id']
        s_key = auth_data['secret']

        # 2. Create DataCenter object
        sdc = DataCenter(location=z_name, key_id=a_key, secret=s_key)

        if req.has_key('server_id'):
            mid = req['server_id']
            machine = sdc.machine(machine_id=mid)
            dic = {}
            dic['server_id'] = machine.id
            dic['private_ip_address'] = machine.private_ips[0]
            if len(machine.public_ips) >= 1:
                dic['floating_ip'] = machine.public_ips[0]
            dic['status'] = machine.status()
            # CPU, Memory, Disk
            if machine.has_key('package'):
                packages = sdc.packages(machine['package'])
                if len(packages) == 1:
                    package = packages[0]
                    dic['cpus'] = package['vcpus']
                    dic['memory'] = package['memory']
                    dic['disk'] = package['disk']
            return dic

        elif req.has_key('name'):
            my_name = req['name']
            machines = sdc.machines(name=my_name)
            self.logger.debug("Detected machine is %s" % len(machines))
            dic = {}
            if len(machines) != 1:
                # Error or ?
                return dic
            machine = machines[0]
            dic['server_id'] = machine.id
            dic['private_ip_address'] = machine.private_ips[0]
            if len(machine.public_ips) >= 1:
                dic['floating_ip'] = machine.public_ips[0]
            dic['status'] = machine.status()
            # CPU, Memory, Disk
            #if machine.has_key('package'):
            #    packages = sdc.packages(machine['package'])
            #    if len(packages) == 1:
            #        package = packages[0]
            #        dic['cpus'] = package['vcpus']
            #        dic['memory'] = package['memory']
            #        dic['disk'] = package['disk']
            return dic
        self.logger.error("No Server founded:%s" % z_name)
 
    def discoverServers(self, auth, zone_id):
        """
        find all servers at zone
        @return: list of server info
        """
        # 1. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)

        auth_data = auth['auth']
        a_key = auth_data['key_id']
        s_key = auth_data['secret']

        # 2. Create DataCenter object
        sdc = DataCenter(location=z_name, key_id=a_key, secret=s_key)
        machines = sdc.machines()
        output = []
        for machine in machines:
            dic = {}
            dic['name'] = machine.name
            dic['server_id'] = machine.id
            dic['private_ip_address'] = machine.private_ips[0]
            if len(machine.public_ips) >= 1:
                dic['floating_ip'] = machine.public_ips[0]
            dic['status'] = machine.state
            # Register Machine
            output.append(dic)

        return output

    def stopServer(self, auth, zone_id, req):
        """
         @param : auth
            {"auth":{
               "key_id":"Key ID",
               "secret":"Secret Key",
                }
            }
        @param: zone_id
        @param: req (Dic)
            {"server_id":"xxx-xxxx-xxx"}
        """
        # 1. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)

        auth_data = auth['auth']
        a_key = auth_data['key_id']
        s_key = auth_data['secret']

        # 2. Create DataCenter object
        sdc = DataCenter(location=z_name, key_id=a_key, secret=s_key)

        if req.has_key('server_id'):
            mid = req['server_id']
            machine = sdc.machine(machine_id=mid)
            # Stop Machine
            machine.stop()
            # Wait state
            machine.poll_until('stopped')
            dic = {}
            dic['status'] = machine.state
            return dic

    def deleteServer(self, auth, zone_id, req):
        """
         @param : auth
            {"auth":{
               "key_id":"Key ID",
               "secret":"Secret Key",
                }
            }
        @param: zone_id
        @param: req (Dic)
            {"server_id":"xxx-xxxx-xxx"}
        """
        # 1. Get Endpoint of Zone
        cloudMgr = self.locator.getManager('CloudManager')
        (r_name, z_name) = cloudMgr._getRegionZone(zone_id)

        auth_data = auth['auth']
        a_key = auth_data['key_id']
        s_key = auth_data['secret']

        # 2. Create DataCenter object
        sdc = DataCenter(location=z_name, key_id=a_key, secret=s_key)

        if req.has_key('server_id'):
            mid = req['server_id']
            try:
                machine = sdc.machine(machine_id=mid)
                # Stop Machine
                machine.stop()
                # Wait state
                machine.poll_until('stopped')

                # Delete Machine
                machine.delete()
                dic = {}
                dic['status'] = machine.state
                return dic
            except:
                self.logger.error("Server does not exist:%s" % mid)
                return {}


    def getServerStatus(self, auth, zone_id, server_id):
        return {'status':'running'}

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
