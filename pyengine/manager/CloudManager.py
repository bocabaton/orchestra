import json
import paramiko
import socket
import time

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
            raise ERROR_EXIST_RESOURCE(key='name', value=params['name'])

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

    def listRegions(self, search):
        region_dao = self.locator.getDAO('region')

        output = []
        (regions, total_count) = region_dao.select(search=search)

        for region in regions:
            region_info = self.locator.getInfo('RegionInfo', region)
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
            search = [{'key':'zone_id', 'value':params['zone_id'], 'option':'eq'},
                      {'key':'key', 'value':kv['key'], 'option':'eq'}]
            (items, total_count) = dao.select(search=search)
            if total_count == 0:
                # Create
                dic = {}
                dic['zone_id'] = params['zone_id']
                dic['key'] = kv['key']
                dic['value'] = kv['value']
                dao.insert(dic)

            else:
                # Delete and Insert
                # TODO: 
                pass

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

        
    ###########################################
    # Cloud Discover
    ###########################################
    def discoverCloud(self, params):
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
        # OpenStack Driver
        if value['type'] == 'openstack':
            driver = self.locator.getManager('OpenStackDriver')
            (output, total_count) = driver.discover(value)
            return (output, total_count)
       
        # TODO: AWS Driver, Joyent Driver


    ###############################################
    # Server 
    ###############################################
    def createServer(self, params, ctx):
        """
        @param:
            {"zone_id":"xxxx-xxx-xxxxx-xxxxx",
             "name":"vm1",
             "floatingIP":True,
             "request":{
                "server":{
                   "name":"vm1",
                   "imageRef":"http://xxxx",
                   "flaverRef":"http://xxxx",
                 }
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
        server = dao.insert(dic)

        # 1. Detect Driver
        #driver = self._getDriver(params['zone_id'])
        driver = self.locator.getManager('OpenStackDriver')
        # 2. Call deploy
        usr_mgr = self.locator.getManager('UserManager')
        platform = 'openstack'
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
        # Update Private IP address
        if created_server.has_key('private_ip_address'):
            self.updateServerInfo(server.server_id, 'private_ip_address', created_server['private_ip_address'])

        # Update server_info
        # ex) server_id from nova
        # Check Server Status
        for i in range(10):
            status = driver.getServerStatus(auth, zone_id, created_server['server_id'])
            if status.has_key('status'):
                if status['status'] == 'ACTIVE':
                    # Can find private address
                    self.updateServerInfo(server.server_id, "private_ip_address", status['private_ip_address'])
                    break
                else:
                    self.logger.info('Wait to active:%s' % status['status'])
                    time.sleep(3)
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
        #########
        # TEMP
        #########
        self.updateServerInfo(server.server_id,'user_id','root')
        self.updateServerInfo(server.server_id,'password','123456')

        return self.locator.getInfo('ServerInfo', server)


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

    #####################################
    # SSH executor
    #####################################

    def executeCmd(self, params):

        # Connect to Node using ssh (ip, user_id, password )
        (tf, ssh) = self._makeSSHClient(params)
        if tf == False:
            return {"error": ssh}

        # We have ssh connection
        self.logger.debug("CMD: %s" % params['cmd'])
        stdin, stdout, stderr = ssh.exec_command(params['cmd'], bufsize=348160, timeout=300, get_pty=False)

        return {'result': stdout.readlines()}

    def _makeSSHClient(self, params):
        # extract information for ssh
        server_info = self.getServerInfo(params['server_id'])
        ip = server_info['floatingip']
       
        if params.has_key('port') == True:
            port = params['port']
        else:
            port = 22
        if params.has_key('user_id') == True:
            user_id = params['user_id']
        else:
            if server_info.has_key('user_id') == True:
                user_id = server_info['user_id']
            else:
                raise ERROR_NOT_FOUND(key='user_id', value='no user_id')
        if params.has_key('password') == True:
            password = params['password']
        else:
            if server_info.has_key('password') == True:
                password = server_info['password']
                AUTH='password'
                
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connected = False
        if AUTH=='password':
            self.logger.debug("Password:%s" % password)
            time.sleep(10)
            try:
                ssh.connect(ip, port, user_id, password)
                connected = True
            except BadHostKeyException as e:
                err_msg = "Bad Host Key Exception"
            except AuthenticationException as e:
                err_msg = "Authentication Exception"
            except SSHException as e:
                err_msg = "SSH Exception"
            except socket.error as e:
                err_msg = "socket error"

        if connected == False and params.has_key('id_rsa'):
            pass

        if connected == False and params.has_key('id_dsa'):
            pass

        if connected == False:
            return (False, "Can not connect")

        return (True, ssh)

