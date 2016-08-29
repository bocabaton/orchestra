import json
import threading

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class StackThread(threading.Thread):
    def __init__(self, driver, template, env, stack_id, ctx):
        threading.Thread.__init__(self)
        self.driver = driver
        self.template = template
        self.env = env
        self.stack_id = stack_id
        self.ctx = ctx

    def run(self):
        self.driver.run(self.template, self.env, self.stack_id, self.ctx)


class PackageManager(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def createPackage(self, params):

        dao = self.locator.getDAO('package') 

        dic = {}
        # Check Product 
        p_dao = self.locator.getDAO('product')
        products = p_dao.getVOfromKey(product_id=params['product_id'])
        if products.count() == 0:
            raise ERROR_INVALID_PARAMETER(key='product_id', value=params['product_id'])
        dic['product']   = products[0]
        dic['version']   = params['version']

        if params.has_key('pkg_type'):
            dic['pkg_type'] = params['pkg_type']

        if params.has_key('template'):
            dic['template'] = params['template']

        if params.has_key('description'):
            dic['description'] = params['description']


        package = dao.insert(dic)

        return self.locator.getInfo('PackageInfo', package)

    def listPackages(self, search, search_or, sort, page):
        dao = self.locator.getDAO('package')

        output = []
        (packages, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)

        for item in packages:
            info = self.locator.getInfo('PackageInfo', item)
            output.append(info)

        return (output, total_count)

    def updatePackage(self, params):
        dao = self.locator.getDAO('package') 

        if not dao.isExist(package_id=params['package_id']):
            raise ERROR_INVALID_PARAMETER(key='package_id', value=params['package_id'])

        dic = {}

        if params.has_key('pkg_type'):
            dic['pkg_type'] = params['pkg_type']

        if params.has_key('template'):
            dic['template'] = params['template']

        if params.has_key('version'):
            dic['version'] = params['version']

        if params.has_key('description'):
            dic['description'] = params['description']


        package = dao.update(params['package_id'], dic, 'package_id')

        return self.locator.getInfo('PackageInfo', package)

    def getPackage(self, params):
        dao = self.locator.getDAO('package')

        packages = dao.getVOfromKey(package_id=params['package_id'])

        if packages.count() == 0:
            raise ERROR_NOT_FOUND(key='package_id', value=params['package_id'])

        return self.locator.getInfo('PackageInfo', packages[0])

    def deletePackage(self, params):
        dao = self.locator.getDAO('package') 

        packages = dao.getVOfromKey(package_id=params['package_id'])

        if packages.count() == 0:
            raise ERROR_NOT_FOUND(key='package_id', value=params['package_id'])

        packages.delete()

        return {}

    ##############################################
    # Stack
    ##############################################
    def deployStack(self, params, ctx):
        """
        @params:
            - name
            - package_id
            - env
        @ctx: context of account
            - ctx['user_id']
            - ctx['xtoken']
            - ctx['name'] : project name
        """

        # find pkg_type, template
        search = {'package_id':params['package_id']}
        info = self.getPackage(search)
        pkg_type = info.output['pkg_type']
        template = info.output['template']
        if params.has_key('env'):
            env = params['env']
        else:
            env = {}
        dao = self.locator.getDAO('stack')
        dic = {}
        # Check Package 
        p_dao = self.locator.getDAO('package')
        packages = p_dao.getVOfromKey(package_id=params['package_id'])
        if packages.count() == 0:
            raise ERROR_INVALID_PARAMETER(key='package_id', value=params['package_id'])
        dic['package']   = packages[0] 
        dic['env'] = json.dumps(env)
        # User
        user_dao = self.locator.getDAO('user')
        users = user_dao.getVOfromKey(user_id=ctx['user_id'])
        if users.count() != 1:
            raise ERROR_NOT_FOUND(key='user_id', value=ctx['user_id'])
        dic['user'] = users[0]

        # Name
        if params.has_key('name'):
            dic['name'] = params['name']
        else:
            dic['name'] = ''
        stack = dao.insert(dic)

        if ctx.has_key('name') == False:
            ctx['name'] = stack.name[:8]

        self.logger.debug("### Stack ID:%s" % stack.stack_id)
        # Update Env
        # TODO: HOST_IP update from config file
        HOST_IP = '127.0.0.1'
        url = 'http://%s/api/v1/catalog/stacks/%s/env' % (HOST_IP, stack.stack_id)
        item = {'METADATA':url}
        self.addEnv2(stack.stack_id, item)

        # Update Env(token)
        # Add Stack ID for provisioning
        item = {'jeju':{'TOKEN':ctx['xtoken'],'STACK_ID':"%s" % stack.stack_id}}
        self.addEnv2(stack.stack_id, item)

        if pkg_type == "bpmn":
            # BPMN Driver
            self.logger.debug("Launch BPMN Driver")
            driver = self.locator.getManager('BpmnDriver')
            thread = StackThread(driver, template, env, stack.stack_id, ctx)
            thread.start()
            #driver.run(template, env, stack.stack_id)
        elif pkg_type == "docker-compose":
            # Docker-Compose
            self.logger.debug("Launch Docker-Compose driver")
            driver = self.locator.getManager('DockerComposeDriver')
            self.logger.debug(driver)
            thread = StackThread(driver, template, env, stack.stack_id, ctx)
            thread.start()

        return self.getStackByID(stack.stack_id)

    def listStacks(self, search, search_or, sort, page):
        dao = self.locator.getDAO('stack')

        output = []
        (stacks, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)

        for item in stacks:
            info = self.locator.getInfo('StackInfo', item)
            output.append(info)
        return (output, total_count)


    def getStack(self, params):
        return self.getStackByID(params['stack_id'])

    def deleteStack(self, params):
        # TODO: Delete Servers first
        stack_id = params['stack_id']
        # 1. Find Instance related with stack
        #    Delete instances
        c_mgr = self.locator.getManager('CloudManager')
        c_mgr.deleteServersByStackID(stack_id)
        
        # 2. Delete Stack DB
        self._deleteStack(stack_id)
        return {}

    def _deleteStack(self, stack_id):
        dao = self.locator.getDAO('stack')
        stacks = dao.getVOfromKey(stack_id=stack_id)
        if stacks.count() == 0:
            raise ERROR_NOT_FOUND(key='stack_id', value=stack_id)
        stacks.delete()

    def getStackByID(self, stack_id):
        dao = self.locator.getDAO('stack')

        stacks = dao.getVOfromKey(stack_id=stack_id)

        if stacks.count() == 0:
            raise ERROR_NOT_FOUND(key='stack_id', value=stack_id)

        return self.locator.getInfo('StackInfo', stacks[0])


    def getEnv(self, stack_id):
        """
        return: dict of env
        """
        dao = self.locator.getDAO('stack')

        stacks = dao.getVOfromKey(stack_id=stack_id)
        if stacks.count() == 0:
            raise ERROR_NOT_FOUND(key='stack_id', value=stack_id)

        return self.locator.getInfo('StackInfo', stacks[0])


    def getEnv2(self, stack_id, key):
        """
        get value of env
        @param:
            - stack_id
            - key: string for key

        @return: dic
        """
        info = self.getEnv(stack_id)
        env = info.output['env']
        if env.has_key(key):
            return env[key]
        else:
            return {}

    def addEnv(self, params):
        """
        @params:
            {"add" : {'key':'value'}}
        """
        stack_id = params['stack_id']
        info = self.getEnv(stack_id)

        env = info.output['env']
        self.logger.debug("Previous Env: %s" % env)
        keys = params['add'].keys()
        value = params['add']
        for key in keys:
            if env.has_key(key) == False:
                env.update(params['add'])
            else:
                # Env has already key and dictionary type
                if type(env[key]) == dict and type(value[key]) == dict:
                    value1 = env[key]
                    value1.update(value[key])
                
        self.logger.debug("Next Env: %s" % env)

        dic = {}
        dic['env'] = json.dumps(env)
        dao = self.locator.getDAO('stack')
        stack = dao.update(stack_id, dic, 'stack_id')

        return self.locator.getInfo('StackInfo', stack)

    def addEnv2(self, stack_id, item):
        """
        @param:
            - stack_id
            - item: dictionary for data
        """
        params = {'stack_id':stack_id, 'add':item}
        return self.addEnv(params)

    def updateStackState(self, stack_id, state):
        """
        @params:
            - stack_id
            - state : string of state
        """
        dic = {}
        dic['state'] = state
        dao = self.locator.getDAO('stack')
        stack = dao.update(stack_id, dic, 'stack_id')
        return self.locator.getInfo('StackInfo', stack)

