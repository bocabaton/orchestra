import datetime
import os

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class UserManager(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def createUser(self, params):
        user_dao = self.locator.getDAO('user') 

        if user_dao.isExist(user_id=params['user_id']):
            raise ERROR_EXIST_RESOURCE(key='user_id', value=params['user_id'])

        if not utils.checkIDFormat(params['user_id']):
            raise ERROR_INVALID_ID_FORMAT()

        if not utils.checkPasswordFormat(params['password']):
            raise ERROR_INVALID_PASSWORD_FORMAT()

        dic = {}
        dic['user_id'] = params['user_id']
        dic['password'] = make_password(params['password'])

        if params.has_key('name'):
            dic['name'] = params['name']

        if params.has_key('email'):
            dic['email'] = params['email']

        if params.has_key('language'):
            dic['language'] = params['language']
        else:
            dic['language'] = self.GLOBAL_CONF['DEFAULT_LANGUAGE']

        if params.has_key('timezone'):
            dic['timezone'] = params['timezone']
        else:
            dic['timezone'] = self.GLOBAL_CONF['DEFAULT_TIMEZONE']

        if params.has_key('group_id'):
            group_dao = self.locator.getDAO('group')

            groups = group_dao.getVOfromKey(uuid=params['group_id'])

            if groups.count() == 0:
                raise ERROR_INVALID_PARAMETER(key='group_id', value=params['group_id'])

            dic['group'] = groups[0]

        user = user_dao.insert(dic)

        return self.locator.getInfo('UserInfo', user)

    def updateUser(self, params):
        user_dao = self.locator.getDAO('user') 

        if not user_dao.isExist(user_id=params['user_id']):
            raise ERROR_INVALID_PARAMETER(key='user_id', value=params['user_id'])

        dic = {}

        if params.has_key('password'):
            if not utils.checkPasswordFormat(params['password']):
                raise ERROR_INVALID_PASSWORD_FORMAT()

            dic['password'] = make_password(params['password'])

        if params.has_key('name'):
            dic['name'] = params['name']

        if params.has_key('state'):
            dic['state'] = params['state']

        if params.has_key('email'):
            dic['email'] = params['email']

        if params.has_key('language'):
            dic['language'] = params['language']

        if params.has_key('timezone'):
            dic['timezone'] = params['timezone']

        if params.has_key('group_id'):
            group_dao = self.locator.getDAO('group')

            groups = group_dao.getVOfromKey(uuid=params['group_id'])

            if groups.count() == 0:
                raise ERROR_INVALID_PARAMETER(key='group_id', value=params['group_id'])

            dic['group'] = groups[0]

        user = user_dao.update(params['user_id'], dic, 'user_id')

        return self.locator.getInfo('UserInfo', user)

    def deleteUser(self, params):
        user_dao = self.locator.getDAO('user') 

        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])

        users.delete()

        return {}

    def enableUser(self, params):
        params['state'] = 'enable'

        return self.updateUser(params)

    def disableUser(self, params):
        params['state'] = 'disable'

        return self.updateUser(params)

    def getUser(self, params):
        user_dao = self.locator.getDAO('user')

        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])

        return self.locator.getInfo('UserInfo', users[0])

    def listUsers(self, search, search_or, sort, page, res_params):
        user_dao = self.locator.getDAO('user')

        if len(res_params) > 0:
            related_parent = []

            for p in res_params:
                if p == 'group_name':
                    related_parent.append('group')
        else:
            # DAO - Join Example
            # parent_model = ['<model_name>']
            # parent_parent_model = ['<model_name.model_name>']
            related_parent = ['group']

        output = []
        (users, total_count) = user_dao.select(search=search, search_or=search_or, sort=sort, page=page, related_parent=related_parent)

        for user in users:
            user_info = self.locator.getInfo('UserInfo', user, res_params=res_params)
            output.append(user_info)

        return (output, total_count)

    def addUserInfo(self, params, tag=None):
        # TODO: encrypt password
        # TODO: Other user can not add user info
        user_dao = self.locator.getDAO('user')
        dao = self.locator.getDAO('user_detail')
        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])
        dic = {}
        dic['user'] = users[0]
        dic['platform'] = params['platform']
        if tag:
            dic['tag'] = tag
        items = params['add']
        secret_content = ""
        for key in items.keys():
            """
            if joyent, user send content of id_rsa
            But we save it as file, and save file path
            """
            if params['platform'] == 'joyent' and key == 'secret_content':
                dic['key'] = 'secret'
                dic['value'] = self._makeJoyentSecret(params['user_id'], items[key])
                # for Docker Cert
                secret_content = items[key]
            else:
                dic['key'] = key
                dic['value'] = items[key]
            info = dao.insert(dic)
        # Docker cert for Joyent
        if params['platform'] == "joyent":
            self._makeJoyentDockerCert(params['user_id'], secret_content)

        return {}

    def _makeJoyentSecret(self, user_id, secret_content):
        """
        Save joyent account at specific directory
        """
        # TODO: change global configuration
        ACCOUNT_DIR = "/var/www/users"

        user_dir = "%s/%s" % (ACCOUNT_DIR, user_id)
        joyent_dir = "%s/joyent" % user_dir

        # Directory Check
        if not os.path.exists(ACCOUNT_DIR):
            os.mkdir(ACCOUNT_DIR)
            os.chmod(ACCOUNT_DIR, 0700)
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)
            os.chmod(user_dir, 0700)
        if not os.path.exists(joyent_dir):
            os.mkdir(joyent_dir)
            os.chmod(joyent_dir, 0700)
        
        secret = "%s/id_rsa" % joyent_dir
        if os.path.exists(secret):
            os.rename(secret, "%s.%s" % (secret, datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))
        fp = open(secret, 'w')
        fp.write(secret_content)
        fp.close()

        return secret

    def _makeJoyentDockerCert(self, user_id, cert_pem):
        """
        Create DOCKER_CERT_PATH for  Joyent
        """
        # TODO: change global configuration
        ACCOUNT_DIR = "/var/www/users"

        user_dir = "%s/%s" % (ACCOUNT_DIR, user_id)
        joyent_dir = "%s/joyent" % user_dir

        docker_dir = "%s/docker" % joyent_dir

        # Directory Check
        if not os.path.exists(ACCOUNT_DIR):
            os.mkdir(ACCOUNT_DIR)
            os.chmod(ACCOUNT_DIR, 0700)
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)
            os.chmod(user_dir, 0700)
        if not os.path.exists(joyent_dir):
            os.mkdir(joyent_dir)
            os.chmod(joyent_dir, 0700)
        if not os.path.exists(docker_dir):
            os.mkdir(docker_dir)
            os.chmod(docker_dir, 0700)

        # Download ca.pem
        ca_url = ["https://us-east-1.docker.joyent.com:2376/ca.pem","https://us-west-1.docker.joyent.com:2376/ca.pem"]
        ca_path = "%s/ca.pem" % docker_dir
        import requests
        for i in ca_url:
            response = requests.get(i, verify=False)
            if response.status_code == 200:
                fp = open(ca_path, 'w')
                fp.write(response.text)
                fp.close()
                break
            else:
                self.logger.warning("Fail to get joyent ca.pem from %s" % i)
        os.chmod(ca_path, 0400)

        # Update key.pem
        key_path = "%s/key.pem" % docker_dir
        fp = open(key_path, 'w')
        fp.write(cert_pem)
        fp.close()
        os.chmod(key_path, 0400)

        # Create CSR
        csr_path = "%s/docker.csr" % docker_dir
        # Get Joyent account
        j_account = self._getJoyentUserAccount(user_id)
        cmd = "openssl req -new -key %s -out %s -subj \"/CN=%s\"" % (key_path, csr_path, j_account)
        self.logger.debug("Execute:%s" % cmd)
        os.system(cmd)
        os.chmod(csr_path, 0400)

        # Create cert.pem
        cert_path = "%s/cert.pem" % docker_dir
        cmd = "openssl x509 -req -days 365 -in %s -signkey %s -out %s" % (csr_path, key_path, cert_path)
        self.logger.debug("Execute:%s" % cmd)
        os.system(cmd)
        os.chmod(cert_path, 0400)

        # Register to DB
        p = {'user_id':user_id, 'add': {'DOCKER_CERT_PATH':docker_dir}, 'platform':'docker'}
        self.addUserInfo(p, tag='joyent')

         
    def getUserInfo(self, params):
        # TODO: decrypt password
        # TODO: Other user can not get user info

        user_dao = self.locator.getDAO('user')
        dao = self.locator.getDAO('user_detail')
        users = user_dao.getVOfromKey(user_id=params['get'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])

        search = [{'key':'user_id','value':params['get'],'option':'eq'},
                    {'key':'platform','value':params['platform'],'option':'eq'}]
        self.logger.debug("search:%s" % search)
        search_or = []
        sort = {}
        page = {}
        (items, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)
        output = {}
        for item in items:
            self.logger.debug(item)
            key = item.key
            value = item.value
            output[key] = value
        result = {}
        self.logger.debug("output:%s" % output)
        #TODO: for each platform, has specific format
        if params['platform'] == 'openstack':
            result['auth'] = {
                'tenantName':output['tenantName'],
                'passwordCredentials':{
                    'username':output['username'],
                    'password':output['password']
                }
            }
        elif params['platform'] == 'aws':
            result['auth'] = {
                'access_key_id':output['access_key_id'],
                'secret_access_key':output['secret_access_key']
                }

        elif params['platform'] == 'joyent':
            result['auth'] = {
                'key_id':output['key_id'],
                'secret':output['secret']
                }
 
        elif params['platform'] == 'bare-metal':
            # TODO: what should we do?
            pass

        return result

    def _getJoyentUserAccount(self, user_id):
        user_dao = self.locator.getDAO('user')
        dao = self.locator.getDAO('user_detail')
        users = user_dao.getVOfromKey(user_id=user_id)

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=user_id)

        search = [{'key':'user_id','value':user_id,'option':'eq'},
                    {'key':'platform','value':'joyent','option':'eq'},
                    {'key':'key', 'value':'key_id', 'option':'eq'}]
        self.logger.debug("search:%s" % search)
        search_or = []
        sort = {}
        page = {}
        (items, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)
        if total_count == 1:
            a_str = items[0].value
            items = a_str.split("/")
            return items[1]

        raise ERROR_NOT_FOUND(key='key', value=key)

    def getDockerCertPath(self, user_id, tag=None):
        user_dao = self.locator.getDAO('user')
        dao = self.locator.getDAO('user_detail')
        users = user_dao.getVOfromKey(user_id=user_id)

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=user_id)

        search = [{'key':'user_id','value':user_id,'option':'eq'},
                    {'key':'platform','value':'docker','option':'eq'},
                    {'key':'key', 'value':'DOCKER_CERT_PATH', 'option':'eq'}]
        self.logger.debug("search:%s" % search)
        search_or = []
        sort = {}
        page = {}
        (items, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)
        for i in items:
            if tag:
                if tag == i.tag:
                    return i.value
            else:
                return i.value
            
        return None


    def listUserInfo(self, params):
        dao = self.locator.getDAO('user_detail')
        user_dao = self.locator.getDAO('user')
        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])

        output_list = []
        # OpenStack
        search = [{'key':'user_id','value':params['user_id'],'option':'eq'},
                    {'key':'platform', 'value':'openstack', 'option':'eq'}]
        self.logger.debug("search:%s" % search)
        search_or = []
        sort = {}
        page = {}
        (items, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)
        output = {}
        for item in items:
            self.logger.debug(item)
            key = item.key
            value = item.value
            output[key] = value
        if total_count > 0:
            result = {}
            result['platform'] = 'openstack'
            result['auth'] = "%s/%s" % (output['tenantName'],output['username'])
            output_list.append(result)

        # AWS
        search = [{'key':'user_id','value':params['user_id'],'option':'eq'},
                    {'key':'platform', 'value':'aws', 'option':'eq'}]
        self.logger.debug("search:%s" % search)
        search_or = []
        sort = {}
        page = {}
        (items, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)
        output = {}
        for item in items:
            self.logger.debug(item)
            key = item.key
            value = item.value
            output[key] = value
        result = {}
        if total_count > 0:
            result = {}
            result['platform'] = 'aws'
            result['auth'] = output['access_key_id']
            output_list.append(result)

        # Joyent
        search = [{'key':'user_id','value':params['user_id'],'option':'eq'},
                    {'key':'platform', 'value':'joyent', 'option':'eq'}]
        self.logger.debug("search:%s" % search)
        search_or = []
        sort = {}
        page = {}
        (items, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)
        output = {}
        for item in items:
            self.logger.debug(item)
            key = item.key
            value = item.value
            output[key] = value
        result = {}
        if total_count > 0:
            result = {}
            result['platform'] = 'joyent'
            result['auth'] = output['key_id']
            output_list.append(result)

        # TODO: When you add more cloud account

        output = {'total_count':len(output_list), 'results':output_list}
        return output

        
    ############################
    # Keypair
    ############################
    def addUserKeypair(self, params):
        # TODO: encrypt password
        # TODO: Other user can not add user info
        user_dao = self.locator.getDAO('user')
        dao = self.locator.getDAO('user_keypair')
        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])
        item = params['add']
        if item.has_key('name') == False:
            raise ERROR_REQUIRED_PARAM(key='add.name')
        if item.has_key('key_type') == False:
            raise ERROR_REQUIRED_PARAM(key='add.key_type')
        if item.has_key('value') == False:
            raise ERROR_REQUIRED_PARAM(key='add.value')

        dic = {}
        dic['user'] = users[0]
        dic['name'] = item['name']
        dic['key_type'] = item['key_type']
        dic['value'] = item['value']
        info = dao.insert(dic)
        return {}

    def getUserKeypair(self, params):
        dao = self.locator.getDAO('user_keypair')

        user_dao = self.locator.getDAO('user')
        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])

        search = [{'key':'name','value':params['get'],'option':'eq'}]
        self.logger.debug("search:%s" % search)
        search_or = []
        sort = {}
        page = {}
        (items, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)
        if total_count == 0:
            raise ERROR_NOT_FOUND(key='name', value=params['get'])
        item = items[0]
        output = {}
        output['name'] = item.name
        output['key_type'] = item.key_type
        output['value'] = item.value
        return output
