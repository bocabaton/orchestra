import json
import paramiko
import socket
import time
import StringIO

from paramiko.ssh_exception import *

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class CloudManager(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    ##########################################
    # Region
    ##########################################
    def createRegion(self, params):
        region_dao = self.locator.getDAO('region') 

        if region_dao.isExist(name=params['name']):
            return self.getRegionByName(params)
            #raise ERROR_EXIST_RESOURCE(key='name', value=params['name'])

        dic = {}
        dic['name'] = params['name']
        region = region_dao.insert(dic)

        return self.locator.getInfo('RegionInfo', region)

    def updateRegion(self, params):
        region_dao = self.locator.getDAO('region') 

        if not region_dao.isExist(region_id=params['region_id']):
            raise ERROR_INVALID_PARAMETER(key='region_id', value=params['region_id'])

        dic = {}

        if params.has_key('name'):
            dic['name'] = params['name']

        region = region_dao.update(params['region_id'], dic, 'region_id')

        return self.locator.getInfo('RegionInfo', region)

    def deleteRegion(self, params):
        region_dao = self.locator.getDAO('region') 

        regions = region_dao.getVOfromKey(region_id=params['region_id'])

        if regions.count() == 0:
            raise ERROR_NOT_FOUND(key='region_id', value=params['region_id'])

        # TODO: Delete Zones
        # call deleteZone
        search = [{'key':'region_id','value':params['region_id'],'option':'eq'}]
        (infos, total_count) = self.listZones(search)
        for info in infos:
            zone_id = info.output['zone_id']
            param = {'zone_id':zone_id}
            self.deleteZone(param)
       
        regions.delete()

        return {}

    def getRegion(self, params):
        region_dao = self.locator.getDAO('region')

        regions = region_dao.getVOfromKey(region_id=params['region_id'])

        if regions.count() == 0:
            raise ERROR_NOT_FOUND(key='region_id', value=params['region_id'])

        return self.locator.getInfo('RegionInfo', regions[0])

    def getRegionByName(self, params):
        region_dao = self.locator.getDAO('region')

        regions = region_dao.getVOfromKey(name=params['name'])

        if regions.count() == 0:
            raise ERROR_NOT_FOUND(key='name', value=params['name'])

        return self.locator.getInfo('RegionInfo', regions[0])


    def listRegions(self, search, brief=False):
        region_dao = self.locator.getDAO('region')

        output = []
        (regions, total_count) = region_dao.select(search=search)

        for region in regions:
            region_info = self.locator.getInfo('RegionInfo', region)
            # Brief
            if brief == True:
                # get zone
                # get server list
                total_servers = 0
                z_params = [{'key':'region_id','value':region_info.output['region_id'],'option':'eq'}]
                (zones, total_zones) = self.listZones(z_params)
                for zone in zones:
                    s_params = [{'key':'zone_id','value':zone.output['zone_id'],'option':'eq'}]
                    (servers, total) = self.listServers(s_params)
                    total_servers = total_servers + total
                dic = {'total_servers':total_servers, 'total_zones':total_zones}
                region_info.output['brief'] = dic
            output.append(region_info)

        return (output, total_count)

    ##########################################
    # Zone
    ##########################################
    def createZone(self, params):

        zone_dao = self.locator.getDAO('zone')
        dic = {}
        dic['name'] = params['name']

        if params.has_key('region_id'):
            region_dao = self.locator.getDAO('region')
            regions = region_dao.getVOfromKey(region_id=params['region_id'])
            if regions.count() == 0:
                raise ERROR_INVALID_PARAMETER(key='region_id', value=params['region_id'])
            dic['region'] = regions[0]

        dic['zone_type'] = params['zone_type']
        zone = zone_dao.insert(dic)

        return self.locator.getInfo('ZoneInfo', zone)

    def updateZone(self, params):
        zone_dao = self.locator.getDAO('zone') 

        if not zone_dao.isExist(zone_id=params['zone_id']):
            raise ERROR_INVALID_PARAMETER(key='zone_id', value=params['zone_id'])

        dic = {}

        if params.has_key('name'):
            dic['name'] = params['name']

        zone = zone_dao.update(params['zone_id'], dic, 'zone_id')

        return self.locator.getInfo('ZoneInfo', zone)

    def deleteZone(self, params):
        zone_dao = self.locator.getDAO('zone') 

        zones = zone_dao.getVOfromKey(zone_id=params['zone_id'])

        if zones.count() == 0:
            raise ERROR_NOT_FOUND(key='zone_id', value=params['zone_id'])

        zones.delete()

        return {}

    def getZone(self, params):
        zone_dao = self.locator.getDAO('zone')

        zones = zone_dao.getVOfromKey(zone_id=params['zone_id'])

        if zones.count() == 0:
            raise ERROR_NOT_FOUND(key='zone_id', value=params['zone_id'])

        return self.locator.getInfo('ZoneInfo', zones[0])

    def listZones(self, search):
        zone_dao = self.locator.getDAO('zone')

        output = []
        (zones, total_count) = zone_dao.select(search=search)

        for zone in zones:
            zone_info = self.locator.getInfo('ZoneInfo', zone)
            output.append(zone_info)

        return (output, total_count)

    def createZoneDetail(self, params):
        """
        @param
        [{'key':'k1','value':'v1'}]
        """
        dao = self.locator.getDAO('zone_detail')
        for kv in params['create']:
            self.logger.debug("Create")
            self.logger.debug(kv)
            search = [{'key':'zone_id', 'value':params['zone_id'], 'option':'eq'},
                      {'key':'key', 'value':kv['key'], 'option':'eq'}]
            (items, total_count) = dao.select(search=search)
            if total_count == 0:
                # Create
                z_dao = self.locator.getDAO('zone')
                zones = z_dao.getVOfromKey(zone_id=params['zone_id'])
                if zones.count() != 1:
                    raise ERROR_INVALID_PARAMETER(key='zone_id', value=params['zone_id'])

                dic = {}
                dic['zone'] = zones[0]
                dic['key'] = kv['key']
                dic['value'] = kv['value']
                dao.insert(dic)

            else:
                # Delete and Insert
                # TODO: 
                pass

    def _getZoneDetail(self, zone_id):
        """
        @param: zone_id
        @description: get zone detail for driver
        @return: dictionary of zone_detail 
        """
        dao = self.locator.getDAO('zone_detail')
        details = dao.getVOfromKey(zone_id=zone_id)
        dic = {}
        for detail in details:
            dic[detail.key] = detail.value
        return dic

    def _getZonePlatform(self, zone_id):
        """
        @return: platform name
        """
        param = {'zone_id':zone_id}
        zone_info = self.getZone(param)
        return zone_info.output['zone_type']
 
    def _getRegionZone(self, zone_id):
        """
        @param: zone_id
        @return: (region_name, zone_name)
        """
        param = {'zone_id':zone_id}
        zone_info = self.getZone(param)
        param = {'region_id':zone_info.output['region_id']}
        region_info = self.getRegion(param)
        return (region_info.output['name'], zone_info.output['name'])

    def syncZone(self, params, ctx=None):
        """ sync server information

        Param:
            params: {'zone_id':'xxxxx'}
            ctx: {'user_id':'xxxx'}
        Return:
        """
        # List Servers at zone (A)

        # Discover Servers at zone (B)

        # Add Servers (B-A)

        # Change state (A-B)

        # Return servers at zone
 
    ###########################################
    # Cloud Discover
    ###########################################
    def discoverCloud(self, params, ctx=None):
        """
        params:
        {"discover": {
            "type":"openstack",
            "keystone":"http://10.1.0.1:5000/v2.0",
            "auth":{
               "tenantName":"choonho.son",
               "passwordCredentials":{
                  "username": "choonho.son",
                  "password": "123456"
               }
            }
        }
        """
        value = params['discover']
        if value.has_key('type') == False:
            raise ERROR_INVALID_PARAMETER(key='discover', value=params['discover'])

        if value.has_key('auth') == False:
            # Discover Auth from ctx
            auth_params = {'get':ctx['user_id'], 'platform':value['type']}
            usr_mgr = self.locator.getManager('UserManager')
            auth = usr_mgr.getUserInfo(auth_params)
            value.update(auth)
 
        # OpenStack Driver
        if value['type'] == 'openstack':
            driver = self.locator.getManager('OpenStackDriver')
            (output, total_count) = driver.discover(value, ctx)
            return (output, total_count)

        """
        {"discover": {
            "type":"aws",
            "auth":{
               "access_key_id":"aws access key id",
               "secret_access_key":"aws secret access key"
            }
        }
        """
        if value['type'] == 'aws':
            driver = self.locator.getManager('AwsDriver')
            (output, total_count) = driver.discover(value, ctx)
            return (output, total_count)

        # TODO: GCE Driver, Joyent Driver
        """
        {"discover": {
            "type":"joyent",
            "auth":{
               "key_id":"/{account}/keys/{key_id_name}",
               "secret_access_key":"/root/.ssh/joyent_id_rsa"
            }
        }
        """
        if value['type'] == 'joyent':
            driver = self.locator.getManager('JoyentDriver')
            (output, total_count) = driver.discover(value, ctx)
            return (output, total_count)

    def discoverServers(self, params, ctx):
        """
        discover Servers based on auth
        @params:
            {'zone_id':xxxxxx}
        """
        # Discover Auth from ctx
        auth_params = {'get':ctx['user_id'], 'platform':value['type']}
        usr_mgr = self.locator.getManager('UserManager')
        auth = usr_mgr.getUserInfo(auth_params)

        zone_id = params['zone_id']
        (driver, platform) = self._getDriver(zone_id)
        servers = driver.discoverServers(auth, zone_id)

    ###############################################
    # Server 
    ###############################################
    def registerServerByServerInfo(self, zone_id, discovered_server, ctx):
        """
        @params:
            discovered_server : dictionary
                server_info['server_id']
                server_info['private_ip_address']
                server_info['floating_ip']
        """
        # Create DB first
        dao = self.locator.getDAO('server')
        dic = {}
        if discovered_server.has_key('name'):
            dic['name'] = discovered_server['name']
        else:
            dic['name'] = ''
        dic['cpus'] = 0
        dic['memory'] = 0
        dic['disk'] = 0
        if discovered_server.has_key('status'):
            dic['status'] = discovered_server['status']
        else:
            dic['status'] = 'unknown'
        if zone_id:
            z_dao = self.locator.getDAO('zone')
            zones = z_dao.getVOfromKey(zone_id=zone_id)
            if zones.count() == 0:
                raise ERROR_INVALID_PARAMETER(key='zone_id', value=zone_id)
            dic['zone'] = zones[0]
        if ctx:
            # Update User
            user_id = ctx['user_id']
            u_dao = self.locator.getDAO('user')
            users = u_dao.getVOfromKey(user_id=user_id)
            if users.count() != 1:
                raise ERROR_INVALID_PARAMETER(key='user_id', value=user_id)
            dic['user'] = users[0]
 
        server = dao.insert(dic)

        self.updateServerInfo(server.server_id, 'server_id', discovered_server['server_id'])
        # Update Private IP address
        if discovered_server.has_key('private_ip_address'):
            self.updateServerInfo(server.server_id, 'private_ip_address', discovered_server['private_ip_address'])
        if discovered_server.has_key('floating_ip'):
            self.updateServerInfo(server.server_id, 'floatingip', discovered_server['floating_ip'])


        return self.locator.getInfo('ServerInfo', server)



    def registerServer(self, params, ctx):
        """
        Find Server based on server_id
        then register it

        @param:
            {"zone_id":"xxxx-xxx-xxxxx-xxxxx",
             "name":"vm1",
             "floatingIP":True,
             "key_name":"my_keypair_name",
             "stack_id":"xxx-xxxx-xxxxxx",
             "register":True,
             "request":{
                "server_id":"xxxx-xxxx-xxxxx"
              }
            }

         @ctx: context
            ctx['user_id']

        """
        # Update DB first
        dao = self.locator.getDAO('server')
        dic = {}
        dic['name'] = params['name']
        if params.has_key('zone_id'):
            z_dao = self.locator.getDAO('zone')
            zones = z_dao.getVOfromKey(zone_id=params['zone_id'])
            if zones.count() == 0:
                raise ERROR_INVALID_PARAMETER(key='zone_id', value=params['zone_id'])
            dic['zone'] = zones[0]

        # Update User
        u_dao = self.locator.getDAO('user')
        users = u_dao.getVOfromKey(user_id=ctx['user_id'])
        if users.count() != 1:
            raise ERROR_INVALID_PARAMETER(key='user_id', value=ctx['user_id'])
        dic['user'] = users[0]

        server = dao.insert(dic)

        # 1. Detect Driver
        (driver, platform) = self._getDriver(params['zone_id'])
        # 2. Call deploy
        usr_mgr = self.locator.getManager('UserManager')
        auth_params = {'get':ctx['user_id'], 'platform':platform}
        self.logger.debug("auth:%s" % auth_params)
        auth = usr_mgr.getUserInfo(auth_params)
        #auth = {"auth":{
        #    "tenantName":"choonho.son",
        #    "passwordCredentials":{
        #        "username": "choonho.son",
        #        "password": "123456"
        #    }
        #}
        #}
        zone_id = params['zone_id']
        """
        'req': {'server_id':'xxxx-xxxx-xxxxx'}
        """
        req=params['request']
        discovered_server = driver.discoverServer(auth, zone_id, req)
        self.logger.debug("Discovered server:%s" % discovered_server)
 
        # Update server_info
        # Detect server information
        # params['request']
        # @private_ip_address
        # @public_ip_address
        # 
        self.updateServerInfo(server.server_id, 'server_id', discovered_server['server_id'])
        # Update Private IP address
        if discovered_server.has_key('private_ip_address'):
            self.updateServerInfo(server.server_id, 'private_ip_address', discovered_server['private_ip_address'])
        if discovered_server.has_key('floating_ip'):
            self.updateServerInfo(server.server_id, 'floatingip', discovered_server['floating_ip'])

        ########################
        # Update Stack ID
        ########################
        if params.has_key('stack_id') == True:
            self.updateServerInfo(server.server_id, 'stack_id', params['stack_id'])

        ##########################
        # Update Server state
        ##########################
        if discovered_server.has_key('status'):
            self.logger.debug("Update Server status:%s" % discovered_server['status'])
            server = self.updateServer(server.server_id, 'status', discovered_server['status'])

        return self.locator.getInfo('ServerInfo', server)

    def createServer(self, params, ctx):
        """
        @param:
            {"zone_id":"xxxx-xxx-xxxxx-xxxxx",
             "name":"vm1",
             "floatingIP":True,
             "key_name":"my_keypair_name",
             "stack_id":"xxx-xxxx-xxxxxx",
             "request":{
                "server":{
                   "name":"vm1",
                   "imageRef":"http://xxxx",
                   "flaverRef":"http://xxxx",
                 }
              }
            }

            # For baremetal
            {"zone_id":"xxxx-xxx-xxxxx-xxxxx",
             "name":"server01",
             "floatingIP":False,
             "key_name":"my_keypair_name",
             "stack_id":"xxxx-xxxx-xxx-xxx",
             "request": {
                "private_ip_address":"192.168.1.1",
             }
            }
        @ctx: context
            ctx['user_id']

        """
       
        # Update DB first
        dao = self.locator.getDAO('server')
        dic = {}
        dic['name'] = params['name']
        dic['cpus'] = 1
        dic['memory'] = 1
        dic['disk'] = 1
        # Update Zone
        if params.has_key('zone_id'):
            z_dao = self.locator.getDAO('zone')
            zones = z_dao.getVOfromKey(zone_id=params['zone_id'])
            if zones.count() == 0:
                raise ERROR_INVALID_PARAMETER(key='zone_id', value=params['zone_id'])
            dic['zone'] = zones[0]
        # Update User
        u_dao = self.locator.getDAO('user')
        users = u_dao.getVOfromKey(user_id=ctx['user_id'])
        if users.count() != 1:
            raise ERROR_INVALID_PARAMETER(key='user_id', value=ctx['user_id'])
        dic['user'] = users[0]
 
        server = dao.insert(dic)

        # 1. Detect Driver
        (driver, platform) = self._getDriver(params['zone_id'])
        # 2. Call deploy
        usr_mgr = self.locator.getManager('UserManager')
        auth_params = {'get':ctx['user_id'], 'platform':platform}
        self.logger.debug("auth:%s" % auth_params)
        auth = usr_mgr.getUserInfo(auth_params)
        #auth = {"auth":{
        #    "tenantName":"choonho.son",
        #    "passwordCredentials":{
        #        "username": "choonho.son",
        #        "password": "123456"
        #    }
        #}
        #}
        zone_id = params['zone_id']
        req = params['request']
        created_server = driver.deployServer(auth, zone_id, req)

        self.updateServerInfo(server.server_id, 'server_id', created_server['server_id'])

        ############################################
        # Post-processing
        # Specific operations based on cloud type
        ############################################
        if platform == "aws":
            # AWS cannot specify instance name.
            driver.updateName(auth, zone_id, server.server_id, params['name'])

        ############################
        # Update server_info table
        ############################
        # Update Private IP address
        if created_server.has_key('private_ip_address'):
            self.updateServerInfo(server.server_id, 'private_ip_address', created_server['private_ip_address'])
        if created_server.has_key('floating_ip'):
            self.updateServerInfo(server.server_id, 'floatingip', created_server['floating_ip'])

        # Update server_info
        # ex) server_id from nova
        # Check Server Status
        if params.has_key('floatingIP') == True and params['floatingIP'] == True:
            for i in range(10):
                status = driver.getServerStatus(auth, zone_id, created_server['server_id'])
                if status.has_key('status'):
                    self.logger.debug("Server Status:%s" % status['status'])
                    if status['status'] == 'ACTIVE' or status['status'] == 'running':
                        # Can find private address
                        self.updateServerInfo(server.server_id, "private_ip_address", status['private_ip_address'])
                        break
                    else:
                        self.logger.info('Wait to active:%s' % status['status'])
                        time.sleep(5)
                else:
                    self.logger.info('Status not found')

        # 3. Floating IP
        if params.has_key('floatingIP') == True:
            self.logger.debug("Call floating IP")
            if params['floatingIP'] == True:
                address = driver.addFloatingIP(auth, zone_id, created_server['server_id'])
                self.updateServerInfo(server.server_id, 'floatingip', address)
        else:
            self.logger.debug("No Floating IP")
        #######################
        # Update Keypair
        #######################
        if params.has_key('key_name') == True:
            # get value of keypair
            req = {'user_id':ctx['user_id'], 'get':params['key_name']}
            k_info = usr_mgr.getUserKeypair(req)
            if platform == "aws":
                key_user_id = "ec2-user"
            elif platform == "openstack":
                key_user_id = "root"
            elif platform == "joyent":
                key_user_id = "root"
            else:
                key_user_id = "root"

            if params.has_key('login_id') == True:
                key_user_id = params['login_id']

            #TODO: GCE
            self.updateServerInfo(server.server_id, 'user_id', key_user_id)
            self.updateServerInfo(server.server_id, 'key_type', k_info['key_type'])
            self.updateServerInfo(server.server_id, k_info['key_type'] , k_info['value'])

        else:
            # TODO: Temporary(Remove)           
            self.updateServerInfo(server.server_id,'user_id','root')
            self.updateServerInfo(server.server_id,'password','123456')

        ########################
        # Update Stack ID
        ########################
        if params.has_key('stack_id') == True:
            self.updateServerInfo(server.server_id, 'stack_id', params['stack_id'])

        #########################
        # Update Server
        # (cpu, memory, disk)
        #########################
        if created_server.has_key('cpus'):
            server = self.updateServer(server.server_id, 'cpus', created_server['cpus'])
        if created_server.has_key('memory'):
            server = self.updateServer(server.server_id, 'memory', created_server['memory'])
        if created_server.has_key('disk'):
            server = self.updateServer(server.server_id, 'disk', created_server['disk'])

        ##########################
        # Update Server state
        ##########################
        if created_server.has_key('status'):
            self.logger.debug("Update Server status:%s" % created_server['status'])
            server = self.updateServer(server.server_id, 'status', created_server['status'])
    
        return self.locator.getInfo('ServerInfo', server)

    def updateServer(self, server_id, key, value):
        """
        update server table field=key, value=value
        @return: server dao
        """
        self.logger.debug("Update Server at %s,%s=%s" % (server_id, key, value))
        server_dao = self.locator.getDAO('server')
        dic = {}
        dic[key] = value
        server = server_dao.update(server_id, dic, 'server_id')
        return server

    def updateServerInfo(self, server_id, key, value):
        """
        update server_info table
        """
        dao = self.locator.getDAO('server_info')
        dic = {}
        s_dao = self.locator.getDAO('server')
        servers = s_dao.getVOfromKey(server_id=server_id)
        dic['server'] = servers[0]
        dic['key'] = key
        dic['value'] = value
        info = dao.insert(dic)

    def getServerInfo(self, server_id):
        """
        return server_info table
        """
        dao = self.locator.getDAO('server_info')
        infos = dao.getVOfromKey(server_id=server_id)
        item = {}
        for info in infos:
            key = info.key
            value = info.value
            item[key] = value
        return item

    def getServerInfo2(self, params):
        """
        @params:
           {'get':key, 'server_id':server_id}
        return server_info item 
        """
        items = self.getServerInfo(params['server_id'])
        for key in items.keys():
            if key == params['get']:
                return {key: items[key]}
        return {}

    def listServersByStackID(self, stack_id):
        """
        Return: list of server_id
        """
        dao = self.locator.getDAO('server_info')
        search = [{'key':'key','value':'stack_id','option':'eq'},
                {'key':'value','value':stack_id, 'option':'eq'}]
        (infos, total_count) = dao.select(search=search)
        s_list = []
        for info in infos:
            s_list.append(info.server_id.urn[9:])
        return s_list

    def listServers(self, search, brief=False):
        server_dao = self.locator.getDAO('server')

        output = []
        (servers, total_count) = server_dao.select(search=search)

        for server in servers:
            server_info = self.locator.getInfo('ServerInfo', server)
            if brief == True:
                server_info2 = self.getServerBrief({'server_id':server_info.output['server_id']})
                #server_info3 = self.locator.getInfo('ServerInfoBrief', server_info2)
                server_info.output['brief'] = server_info2
            output.append(server_info)

        return (output, total_count)

    def getServerBrief(self, params):
        """
        @params:
            {'server_id':xxxxx}
        Assume: server_id is always exist
        """
        server_id = params['server_id']
        s_info = self.getServerInfo(server_id)
        dic = {}
        if s_info.has_key('private_ip_address'):
            dic['private_ip'] = s_info['private_ip_address']
        else:
            dic['private_ip'] = ""
        if s_info.has_key('floatingip'):
            dic['public_ip'] = s_info['floatingip']
        else:
            dic['public_ip'] = ""
        if s_info.has_key('user_id'):
            dic['login_id'] = s_info['user_id']
        else:
            dic['login_id'] = ""
        if s_info.has_key('server_id'):
            dic['server_id'] = s_info['server_id']
        else:
            dic['server_id'] = ""
        if s_info.has_key('stack_id'):
            dic['stack_id'] = s_info['stack_id']
            pmgr = self.locator.getManager('PackageManager')
            stack_info = pmgr.getStackByID(s_info['stack_id'])
            dic['stack_name'] = stack_info.output['name']
        else:
            dic['stack_id'] = ""
            dic['stack_name'] = ""
        return dic


    def deleteServer(self, params, ctx):
        dao = self.locator.getDAO('server') 

        servers = dao.getVOfromKey(server_id=params['server_id'])

        if servers.count() == 0:
            raise ERROR_NOT_FOUND(key='server_id', value=params['server_id'])

        # Update Status to "deleting"
        self.updateServer(servers[0].server_id, 'status', 'deleting')
 
        # 1. Detect Driver
        (driver, platform) = self._getDriver(servers[0].zone_id)
        self.logger.debug("Detected (%s,%s)" % (driver, platform))
 
        # Delete server_info first
        si_dao = self.locator.getDAO('server_info')
        sis = si_dao.getVOfromKey(server=servers[0])

        # Detected server_id at server_info
        param2 = {'get':'server_id', 'server_id':params['server_id']}
        server_info = self.getServerInfo2(param2)
        ignore_driver = False
        if server_info.has_key('server_id') == False:
            #raise ERROR_NOT_FOUND(key='server_id', value=params['server_id'])
            # May be wrong DB, ignore
            self.logger.error("server_info has no server_id:%s" % params['server_id'])
            ignore_driver = True

        # 2. Call delete
        usr_mgr = self.locator.getManager('UserManager')
        auth_params = {'get':ctx['user_id'], 'platform':platform}
        self.logger.debug("auth:%s" % auth_params)
        auth = usr_mgr.getUserInfo(auth_params)
        #auth = {"auth":{
        #    "tenantName":"choonho.son",
        #    "passwordCredentials":{
        #        "username": "choonho.son",
        #        "password": "123456"
        #    }
        #}
        #}
        zone_id = servers[0].zone_id
        self.logger.debug("Server at Zone ID:%s" % zone_id)
        """
        'req': {'server_id':'xxxx-xxxx-xxxxx'}
        """
        if ignore_driver == False:
            req={'server_id':server_info['server_id']}
            deleted_server = driver.deleteServer(auth, zone_id, req)
 
        self.logger.debug("Delete Server Info(%s)" % len(sis))
        sis.delete()

        self.logger.debug("Delete Server(%s)" % len(servers))
        servers.delete()

        return {}

 
    #####################################
    # SSH executor
    #####################################

    def executeCmd(self, params):

        # Connect to Node using ssh (ip, user_id, password )
        TRY_COUNT=5
        for i in range(TRY_COUNT):
            (tf, ssh, user_id) = self._makeSSHClient(params)
            if tf == True:
                break
            self.logger.info("Failed to connect, try again(%s)" % i+1)
            time.sleep(30)

        if tf == False:
            return {"error": ssh}

        # We have ssh connection
        self.logger.debug("CMD: %s" % params['cmd'])

        # Assume, execute as root privileges
        if user_id != "root":
            cmd = "sudo %s" % params['cmd']
        else:
            cmd = params['cmd']
        stdin, stdout, stderr = ssh.exec_command(cmd, bufsize=348160, timeout=300, get_pty=False)

        return {'result': stdout.readlines()}

    def _makeSSHClient(self, params):
        # extract information for ssh
        server_info = self.getServerInfo(params['server_id'])
        
        if server_info.has_key('floatingip'):
            ip = server_info['floatingip']
        elif server_info.has_key('private_ip_address'):
            ip = server_info['private_ip_address']
        else:
            self.logger.info("Can not find IP: %s" % server_info)

        self.logger.debug("SSH IP : %s" % ip)

        if params.has_key('port') == True:
            port = params['port']
        else:
            port = 22
        # User ID
        if params.has_key('user_id') == True:
            user_id = params['user_id']
        else:
            if server_info.has_key('user_id') == True:
                user_id = server_info['user_id']
            else:
                raise ERROR_NOT_FOUND(key='user_id', value='no user_id')
        # Password
        auth_type = "password"
        if params.has_key('password') == True:
            password = params['password']
        elif params.has_key('id_rsa') == True:
            auth_type = 'id_rsa'
            id_rsa = params['id_rsa']
        elif params.has_key('id_dsa') == True:
            auth_type = 'id_dsa'
            id_dsa = params['id_dsa']
        else:
            # Find from server_info
            if server_info.has_key('key_type') == True:
                auth_type = server_info['key_type']
                if auth_type == 'password':
                    password = server_info['password']
                elif auth_type == 'id_rsa':
                    id_rsa = server_info['id_rsa']
                elif auth_type == 'id_dsa':
                    id_dsa = server_info['id_dsa']
 
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connected = False
        self.logger.debug("Auth Type:%s" % auth_type)
        self.logger.debug("User ID:%s" % user_id)
        if auth_type=='password':
            self.logger.debug("Password:%s" % password)
            time.sleep(10)
            try:
                ssh.connect(ip, port, user_id, password)
                connected = True
            except BadHostKeyException as e:
                err_msg = "Bad Host Key Exception"
                connected = False
            except AuthenticationException as e:
                err_msg = "Authentication Exception"
                connected = False
            except SSHException as e:
                err_msg = "SSH Exception"
                connected = False
            except socket.error as e:
                err_msg = "socket error"
                connected = False

        elif auth_type == 'id_rsa':
            # Connect by id_rsa
            try:
                pkey = paramiko.RSAKey.from_private_key(StringIO.StringIO(id_rsa))
                ssh.connect(ip, port, user_id, pkey=pkey)
                connected = True
            except BadHostKeyException as e:
                err_msg = "Bad Host Key Exception"
                connected = False
            except AuthenticationException as e:
                err_msg = "Authentication Exception"
                connected = False
            except SSHException as e:
                err_msg = "SSH Exception"
                connected = False
            except socket.error as e:
                err_msg = "socket error"
                connected = False
                self.logger.debug(e)

        elif auth_type == 'id_dsa':
            # Connect by id_dsa
            try:
                pkey = paramiko.DSSKey.from_private_key(StringIO.StringIO(id_dsa))
                ssh.connect(ip, port, user_id, pkey=pkey)
                connected = True
            except BadHostKeyException as e:
                err_msg = "Bad Host Key Exception"
                connected = False
            except AuthenticationException as e:
                err_msg = "Authentication Exception"
                connected = False
            except SSHException as e:
                err_msg = "SSH Exception"
                connected = False
            except socket.error as e:
                err_msg = "socket error"
                connected = False

        if connected == False:
            self.logger.debug(err_msg)
            return (False, "Can not connect", user_id)

        return (True, ssh, user_id)

    def _getDriver(self, zone_id):
        """
        @params
            - zone_id: zone ID
        @return
            - driver instance of cloud (ex OpenStackDriver, AwsDriver)
            - platform name
        """
        driver_dic = {'openstack':'OpenStackDriver',
                'aws':'AwsDriver',
                'bare-metal':'BaremetalDriver',
                'joyent':'JoyentDriver',
                'docker':'DockerDriver',
            }
        param = {'zone_id':zone_id}
        zone_info = self.getZone(param)
        zone_type = zone_info.output['zone_type']

        return (self.locator.getManager(driver_dic[zone_type]), zone_type)
