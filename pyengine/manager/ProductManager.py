from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class ProductManager(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def createProduct(self, params):

        dao = self.locator.getDAO('product') 

        dic = {}
        # Check Portfolio 
        p_dao = self.locator.getDAO('portfolio')
        portfolios = p_dao.getVOfromKey(portfolio_id=params['portfolio_id'])
        if portfolios.count() == 0:
            raise ERROR_INVALID_PARAMETER(key='portfolio_id', value=params['portfolio_id'])
        dic['portfolio']   = portfolios[0]
        dic['name']             = params['name']
        dic['short_description']= params['short_description']
        dic['description']      = params['description']
        dic['provided_by']      = params['provided_by']

        if params.has_key('vendor'):
            dic['vendor'] = params['vendor']

        product = dao.insert(dic)

        return self.locator.getInfo('ProductInfo', product)

    def listProducts(self, search, search_or, sort, page):
        dao = self.locator.getDAO('product')

        output = []
        (products, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)

        for item in products:
            info = self.locator.getInfo('ProductInfo', item)
            output.append(info)

        return (output, total_count)

    def updateProduct(self, params):
        dao = self.locator.getDAO('product') 

        if not dao.isExist(product_id=params['product_id']):
            raise ERROR_INVALID_PARAMETER(key='product_id', value=params['product_id'])

        dic = {}

        if params.has_key('name'):
            dic['name'] = params['name']

        if params.has_key('short_description'):
            dic['short_description'] = params['short_description']


        if params.has_key('description'):
            dic['description'] = params['description']

        if params.has_key('provided_by'):
            dic['provided_by'] = params['provided_by']

        if params.has_key('vendor'):
            dic['vendor'] = params['vendor']

        product = dao.update(params['product_id'], dic, 'product_id')

        return self.locator.getInfo('ProductInfo', product)

    def getProduct(self, params):
        dao = self.locator.getDAO('product')

        products = dao.getVOfromKey(product_id=params['product_id'])

        if products.count() == 0:
            raise ERROR_NOT_FOUND(key='product_id', value=params['product_id'])

        return self.locator.getInfo('ProductInfo', products[0])

    def deleteProduct(self, params):
        dao = self.locator.getDAO('product') 

        products = dao.getVOfromKey(product_id=params['product_id'])

        if products.count() == 0:
            raise ERROR_NOT_FOUND(key='product_id', value=params['product_id'])

        products.delete()

        return {}


    #####################################################
    # Product Detail                                    #
    # API                                               #
    # - Create/Update Product Detail                    #
    # - Delete Product Detail                           #
    # - Get Product Detail                              #
    #####################################################
    def createProductDetail(self, params):

        p_dao = self.locator.getDAO('product') 

        dic = {}
        # Get Product
        dao = self.locator.getDAO('product')
        products = p_dao.getVOfromKey(product_id=params['product_id'])
        if products.count() == 0:
            raise ERROR_INVALID_PARAMETER(key='product_id', value=params['product_id'])

        dic['product'] = products[0]

        if params.has_key('email'):
            dic['email'] = params['email']
        if params.has_key('support_link'):
            dic['support_link'] = params['support_link']
        if params.has_key('support_description'):
            dic['support_description'] = params['support_description']


        dao = self.locator.getDAO('product_detail')
        if not dao.isExist(product_id=params['product_id']):
            # Insert
            product = dao.insert(dic)
        else:
            # Update
            product = dao.update(params['product_id'], dic, 'product_id')

        return self.locator.getInfo('ProductDetailInfo', product)

    def getProductDetail(self, params):
        dao = self.locator.getDAO('product_detail')

        products = dao.getVOfromKey(product_id=params['product_id'])

        if products.count() == 0:
            raise ERROR_NOT_FOUND(key='product_id', value=params['product_id'])

        return self.locator.getInfo('ProductDetailInfo', products[0])



    def deleteProductDetail(self, params):
        dao = self.locator.getDAO('product_detail') 

        products = dao.getVOfromKey(product_id=params['product_id'])

        if products.count() == 0:
            raise ERROR_NOT_FOUND(key='product_id', value=params['product_id'])

        products.delete()

        return {}


    #########################################################
    # Tag                                                   #
    # API                                                   #
    # - create Tag                                          #
    # - update Tag                                          #
    # - list Tags                                           #
    # - delete Tag                                          #
    #########################################################
    def createTag(self, params):
        p_dao = self.locator.getDAO('product') 

        dic = {}
        # Get Product
        dao = self.locator.getDAO('product')
        # product_uuid is necessary
        if params['create'].has_key('key') == False:
            raise ERROR_INVALID_PARAMETER(key='key', value=params['create']['key'])
        if params['create'].has_key('value') == False:
            raise ERROR_INVALID_PARAMETER(key='value', value=params['create']['value'])


        products = p_dao.getVOfromKey(product_id=params['product_id'])
        if products.count() == 0:
            raise ERROR_INVALID_PARAMETER(key='product_id', value=params['product_id'])

        dic['product'] = products[0]
        dic['key']   = params['create']['key']
        dic['value'] = params['create']['value']

        dao = self.locator.getDAO('tag')
        tag = dao.insert(dic)

        return self.locator.getInfo('TagInfo', tag)

    def updateTag(self, params):
        p_dao = self.locator.getDAO('product') 

        dic = {}
        # Get Product
        dao = self.locator.getDAO('product')
        # product_uuid is necessary
        if params['update'].has_key('uuid') == False:
            raise ERROR_INVALID_PARAMETER(key='uuid', value=params['update']['uuid'])
        if params['update'].has_key('key') == False:
            raise ERROR_INVALID_PARAMETER(key='key', value=params['update']['key'])
        if params['update'].has_key('value') == False:
            raise ERROR_INVALID_PARAMETER(key='value', value=params['update']['value'])

        products = p_dao.getVOfromKey(product_id=params['product_id'])
        if products.count() == 0:
            raise ERROR_INVALID_PARAMETER(key='product_id', value=params['product_id'])

        dic['product'] = products[0]
        dic['key']   = params['update']['key']
        dic['value'] = params['update']['value']

        dao = self.locator.getDAO('tag')

        if not dao.isExist(uuid=params['update']['uuid']):
            raise ERROR_INVALID_PARAMETER(key='uuid', value=params['update']['uuid'])

        tag = dao.update(params['update']['uuid'], dic, 'uuid')

        return self.locator.getInfo('TagInfo', tag)

    def listTags(self, search, search_or, sort, page):
        dao = self.locator.getDAO('tag')

        output = []
        (tags, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)

        for item in tags:
            info = self.locator.getInfo('TagInfo', item)
            output.append(info)

        return (output, total_count)



    def deleteTag(self, params):
        dao = self.locator.getDAO('tag') 

        tags = dao.getVOfromKey(uuid=params['delete'])

        if tags.count() == 0:
            raise ERROR_NOT_FOUND(key='uuid', value=params['delete'])

        tags.delete()

        return {}


