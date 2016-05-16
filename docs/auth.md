# Authentication

## Environment

Keyword | Value | Description
----    | ----  | ----
URL     | http://127.0.0.1/api/v1 | URL for request
USER_ID     | sunshout | user_id for this system
PASSWORD     | 123456 | password for this system
OPENSTACK | True | If you don't want to test OpenStack, change to False
AWS | True | If you don't want to test AWS, change to False
KEYPAIR | True | If you don't want to register keypair change to False

# Reqeust token

~~~python
import requests
import json
import pprint,sys,re

class writer:
    def write(self, text):
        text=re.sub(r'u\'([^\']*)\'', r'\1',text)
        sys.stdout.write(text)

wrt=writer()

pp = pprint.PrettyPrinter(indent=2, stream=wrt)

def show(dic):
    print pp.pprint(dic)

def display(title):
    print "\n"
    print "################# " + '{:20s}'.format(title) + "##############"

header = {'Content-Type':'application/json'}

def makePost(url, header, body):
    r = requests.post(url, headers=header, data=json.dumps(body))
    if r.status_code == 200:
        return json.loads(r.text)
    print r.text
    raise NameError(url)

def makePut(url, header, body):
    r = requests.put(url, headers=header, data=json.dumps(body))
    if r.status_code == 200:
        return json.loads(r.text)
    print r.text
    raise NameError(url)


def makeGet(url, header):
    r = requests.get(url, headers=header)
    if r.status_code == 200:
        return json.loads(r.text)
    print r.text
    raise NameError(url)

def makeDelete(url, header):
    r = requests.delete(url, headers=header)
    if r.status_code == 200:
        return json.loads(r.text)
    print r.text
    raise NameError(url)

user_id='${USER_ID}'
url = '${URL}/token/get'
body = {'user_id':user_id, 'password':'${PASSWORD}'}
token = makePost(url, header, body)
token_id = token['token']

display('Request with token')
url = '${URL}/catalog/products'
header.update({'X-Auth-Token':token_id})
show(makeGet(url, header))


display('Add Cloud User info')
a_url = '${URL}/users/%s/detail' % user_id

if ${OPENSTACK}:
    display('Add OpenStack Cloud User info')
    tenant_name = raw_input('Tenant Name: ')
    username = raw_input('User ID: ')
    password = raw_input('Password: ')
    body = {"add": {"tenantName":tenant_name, "username":username, "password":password},"platform":"openstack"}
    show(makePost(a_url, header, body))


if ${AWS}:
    display('Add AWS Cloud User info')
    a_key = raw_input('AWS Access Key ID: ')
    sa_key = raw_input('AWS Secret Access Key: ')
    body = {'add':{'access_key_id':a_key, 'secret_access_key':sa_key},'platform':'aws'}
    show(makePost(a_url, header, body))

if ${KEYPAIR}:
    display('Add Keypair to User info')
    key_path = raw_input('Key pair file path:')
    fp = open(key_path, 'r')
    k_url = '${URL}/users/%s/keypair' % user_id
    key_name = raw_input('keypair name:')
    body = {'add':{'name':key_name, 'key_type':'id_rsa', 'value':fp.read()}}
    show(makePost(k_url, header, body))
~~~
