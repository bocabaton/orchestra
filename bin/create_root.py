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

def deleteRootUser():
    users = user_dao.getVOfromKey(user_id=ROOT_USER)
    users.delete()

def createRootUser(password):
    dic = {}
    dic['user_id'] = ROOT_USER
    dic['password'] = make_password(password)
    dic['language'] = GLOBAL_CONF['DEFAULT_LANGUAGE']
    dic['timezone'] = GLOBAL_CONF['DEFAULT_TIMEZONE']

    user_dao.insert(dic)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print
        print "Usage: ./create_root.py <password>"
        print
        exit(1)
    else:
        password = sys.argv[1]

    deleteRootUser()

    createRootUser(password)

    print
    print "Success : Create a '%s' user" %(ROOT_USER)
    print
    exit(0)
