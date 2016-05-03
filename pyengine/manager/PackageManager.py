import json

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

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
            - package_id
            - env
        @ctx: context of account
            - ctx['user_id']
            - ctx['xtoken']

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
        stack = dao.insert(dic)

        self.logger.debug("### Stack ID:%s" % stack.stack_id)
        # Update Env
        # TODO: HOST_IP update from config file
        HOST_IP = '127.0.0.1'
        url = 'http://%s/api/v1/catalog/stacks/%s/env' % (HOST_IP, stack.stack_id)
        item = {'METADATA':url}
        self.addEnv2(stack.stack_id, item)

        # Update Env(token)
        item = {'jeju':{'TOKEN':ctx['xtoken']}}
        self.addEnv2(stack.stack_id, item)

        if pkg_type == "bpmn":
            # BPMN Driver
            driver = self.locator.getManager('BpmnDriver')
            driver.run(template, env, stack.stack_id)
        return self.getStackByID(stack.stack_id)

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
