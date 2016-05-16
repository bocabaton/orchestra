#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Root ID
ROOT_USER = 'root'

import os, sys
import django

path = os.path.abspath(__file__ + '/../..')
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyengine.settings")
django.setup()

from django.contrib.auth.hashers import make_password
from pyengine.lib.locator import Locator
from pyengine.lib import config

GLOBAL_CONF = config.getGlobalConfig()

locator = Locator()
user_dao = locator.getDAO('user')

def deleteUser(user_id):
    users = user_dao.getVOfromKey(user_id=user_id)
    users.delete()

def createUser(user_id, password):
    dic = {}
    dic['user_id'] = user_id
    dic['password'] = make_password(password)
    dic['language'] = GLOBAL_CONF['DEFAULT_LANGUAGE']
    dic['timezone'] = GLOBAL_CONF['DEFAULT_TIMEZONE']

    user_dao.insert(dic)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print
        print "Usage: ./create_user.py <user_id> <password>"
        print
        exit(1)
    else:
        user_id = sys.argv[1]
        password = sys.argv[2]

    deleteUser(user_id)

    createUser(user_id, password)

    print
    print "Success : Create a '%s' user" %(user_id)
    print
    exit(0)
