# Create Region

# Environment

Keyword | Value | Description
----    | ----  | ----
URL     | http://127.0.0.1/api/v1 | URL for request
USER_ID | root  | user_id of Orchestra account
PASSWORD| 123456| password of Orchestra account

# Region/Zone

Add Baremetal Server information

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

display('Auth')
url = '${URL}/token/get'
user_id='${USER_ID}'
password='${PASSWORD}'
body = {'user_id':user_id, 'password':password}
token = makePost(url, header, body)
token_id = token['token']
header.update({'X-Auth-Token':token_id})

display('List Regions')
url = '${URL}/provisioning/regions'
show(makeGet(url, header))
region_id = raw_input("Region ID:")

display('List Zones')
url = '${URL}/provisioning/zones?region_id=%s' % region_id
show(makeGet(url, header))
zone_id = raw_input("Zone ID:")

while 1:
    s_url = '${URL}/provisioning/servers'
    name = raw_input("hostname:")
    ip = raw_input("IP address:")
    key_name = raw_input("Key name:")
    req = {'private_ip_address':ip}
    body = {'name':name, 'zone_id':zone_id, 'key_name':key_name, 'request':req}
    server = makePost(s_url, header, body)
    show(server)
    y = raw_input('Add more(y/n)?')
    if y == 'n':
        break
~~~
