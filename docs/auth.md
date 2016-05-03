# Authentication

## Environment

Keyword | Value | Description
----    | ----  | ----
URL     | http://127.0.0.1/api/v1 | URL for request
USER_ID     | sunshout | user_id for this system
PASSWORD     | 123456 | password for this system
TENANT_ID   | choonho.son | OpenStack tenant ID
USER_ID2    | choonho.son | OpenStack User ID
PASSWORD2   | 123456        | OpenStack Password
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
body = {"add": {"tenantName":"${TENANT_ID}", "username":"${USER_ID2}", "password":"${PASSWORD2}"},"platform":"openstack"}
show(makePost(a_url, header, body))

display('Get Cloud User Info')
body = {'get':user_id, 'platform':'openstack'}
show(makePost(a_url, header, body))
~~~
