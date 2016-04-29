#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import crypt, getpass, spwd
import json
import yaml
import random
import hashlib
import re
import rsa
import base64
import string

def db2Dic(db_str):
    dic = {}

    value_arr = db_str.split(';')
    for value in value_arr:
        if value.strip():
            v = value.split(':',1)
            try:
                dic[v[0].strip()] = v[1].strip().encode('utf-8')
            except:
                pass

    return dic

def dic2DB(dic):
    db_str = ''
    for d in dic:
        if type(dic[d]) == type(unicode()):
            db_str += str(d) + ":" + dic[d].encode('utf-8') + ";"
        else:
            db_str += str(d) + ":" + str(dic[d]) + ";"

    return db_str

def db2List(db_str):
    li = []

    value_arr = db_str.split(';')
    for value in value_arr:
        if value.strip():
            try:
                li.append(value.strip().encode('utf-8'))
            except:
                pass

    return li

def list2DB(li):
    db_str = ''
    for l in li:
        if type(l) == type(unicode()):
            db_str += l.encode('utf-8') + ";"
        else:
            db_str += str(l) + ";"

    return db_str

def jsonEncode(data):
    try:
        json_data = json.dumps(data , sort_keys=True)
        return json_data

    except Exception as e:
        print e
        return False

def jsonDecode(json_data):
    try:
        if json_data.strip() == '':
            return {}
        else:
            data = json.loads(json_data)
            return data

    except Exception as e:
        print e
        return False

def loadYAML(yaml_path):
    try:
        with open(yaml_path, 'r') as f:
            return yaml.load(f)

    except Exception as e:
        print e
        return False

def makePassword(length=10):
    pwd = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + '!@#%') for x in range(length-1))
    return pwd + ''.join(random.choice('!@#%') for x in range(1))

def md5Password(password):
    m = hashlib.md5()
    m.update(str(password))
    return m.hexdigest()

def int2IP(intip):
    """
    convert integer IP to dotted format
    ex) 1234455 -> 8.8.8.8
    """
    octet = ''
    for exp in [3,2,1,0]:
        octet = octet + str(intip / ( 256 ** exp )) + "."
        intip = intip % ( 256 ** exp )
    return octet.rstrip('.')

def ip2Int(dotted_ip):
    """
    convert dotted IP to Integer number
    ex) 8.8.8.8 -> 123455
    """
    exp = 3
    intip = 0
    for quad in dotted_ip.split('.'):
        intip = intip + (int(quad) * (256 ** exp))
        exp = exp - 1
    return intip

def subnet2Int(subnet):
    subnet_dic = {
        '255.255.0.0' : 16,
        '255.255.128.0' : 17,
        '255.255.192.0' : 18,
        '255.255.224.0' : 19,
        '255.255.240.0' : 20,
        '255.255.248.0' : 21,
        '255.255.252.0' : 22,
        '255.255.254.0' : 23,
        '255.255.255.0' : 24,
        '255.255.255.128' : 25,
        '255.255.255.192' : 26,
        '255.255.255.224' : 27,
        '255.255.255.240' : 28,
        '255.255.255.248' : 29,
        '255.255.255.252' : 30,
        '255.255.255.254' : 31,
        '255.255.255.255' : 32
    }

    if subnet_dic.has_key(subnet):
        return subnet_dic[subnet]
    else:
        return False

def isValidIpv4(ipaddress):
    ipaddress = ipaddress.strip()
    ip_content_re = re.compile(r'^'+
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9]).'+
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9]).'+
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9]).'+
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9]?[0-9])$'
    )
    if ip_content_re.match(ipaddress):  
        return True
    else:
        return False
    
def checkIDFormat(char):
    pattern_char = '^[a-zA-Z0-9.\-_@#]{4,20}$'

    if re.match(pattern_char, char):
        return True
    else:
        return False

def checkPasswordFormat(password):
    pattern_two_alpha_char = "(?=.*[A-Za-z].*[A-Za-z])"

    pattern_length = "(?=^.{8,20}$)"
    pattern_upper_char = "(?=.*[A-Z])"
    pattern_lower_char = "(?=.*[a-z])"
    pattern_digits = "(?=.*\d)"
    pattern_special_char = "(?=.*[!@#$%&?])"

    # Passwords must be at least 2 alphabet
    if re.match(pattern_two_alpha_char, password) == None:
        return False

    # Passwords must be at least six characters in length. 8 ~ 14
    if re.match(pattern_length, password) == None:
        return False

    """
    Passwords must contain characters from three of the following four categories:
    English uppercase characters (A through Z).
    English lowercase characters (a through z).
    Base 10 digits (0 through 9).
    Non-alphabetic characters (for example, !, @, #, $, %, &, ?).
    """

    count = 0

    if re.match(pattern_upper_char,password):
        count += 1

    if re.match(pattern_lower_char,password):
        count += 1

    if re.match(pattern_digits,password):
        count += 1

    if re.match(pattern_special_char,password):
        count += 1

    if count >= 2:
        return True
    else:
        return False

def sortList(datas, sort_key='name', sort_type='asc'):
    if sort_type == 'desc':
        reverse = True
    else:
        reverse = False

    return sorted(datas, key=lambda k: k[sort_key], reverse=reverse) 

def encryptRSA(value, pubkey_str):
    pubkey = rsa.PublicKey.load_pkcs1(pubkey_str)

    encrypted_value = rsa.encrypt(value, pubkey)

    return base64.b64encode(encrypted_value)

def decryptRSA(value, prikey_str):
    prikey = rsa.PrivateKey.load_pkcs1(prikey_str)

    encrypted_value = base64.b64decode(str(value))

    return rsa.decrypt(encrypted_value, prikey)

if __name__ == '__main__':
    print makePassword()
    pass

    #print loadYAML('../conf/error.conf')
    print loadYAML('../conf/global.conf')
    #print loadYAML('../conf/router.conf')
    #print loadYAML('../conf/plugin.conf')
