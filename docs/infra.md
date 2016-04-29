# Create Region

# Environment

Keyword | Value | Description
----    | ----  | ----
URL     | http://127.0.0.1/api/v1 | URL for request

# Create Test 

## Create Region

~~~python
import requests
import json

headers = {'Content-Type':'application/json'}

def makeRegion(region_name):
    req_body = {'name':region_name}
    url = '${URL}/provisioning/regions'
    print url
    r =requests.post(url, headers=headers, data=json.dumps(req_body))
    print r.text
    result = json.loads(r.text)
    return result['region_id']

def listRegion(option):
    if option:
        url = '${URL}/provisioning/regions%s' % option
    else:
        url = '${URL}/provisioning/regions'
    r = requests.get(url, headers=headers)
    print r.text
    return r.text

def listZones(option):
    if option:
        url = '${URL}/provisioning/zones%s' % option
    else:
        url = '${URL}/provisioning/zones'
    r = requests.get(url, headers=headers)
    print r.text
    return r.text


def deleteRegion(region_id):
    url = '${URL}/provisioning/regions/%s' % region_id
    r = requests.delete(url, headers=headers)
    print r.text

r_id1 = makeRegion('Test Region #1')
listRegion(None)
r = listZones(None)
r2 = json.loads(r)
#deleteRegion(r2['results'][0]['region_id'])
~~~

# Discovery Region

We can automatically discover zone information

~~~python
import requests
import json
import pprint

hdr = {'Content-Type':'application/json'}

def makeDiscover():
    url = '${URL}/provisioning/discover'
    r_data = {
        "discover": {
            "type":"openstack",
            "keystone":"http://10.1.0.1:5000/v2.0",
            "auth":{
               "tenantName":"choonho.son",
               "passwordCredentials":{
                  "username": "choonho.son",
                  "password": "123456"
               }
            }
        }
    }
    r = requests.post(url,headers=hdr, data=json.dumps(r_data))
    pp = pprint.PrettyPrinter(indent=2)
    print pp.pprint(json.loads(r.text))

makeDiscover()

def listZones(option):
    if option:
        url = '${URL}/provisioning/zones%s' % option
    else:
        url = '${URL}/provisioning/zones'
    r = requests.get(url, headers=hdr)
    print r.text
    return r.text
listZones(None)
~~~ 


# Create Server

~~~python
import requests
import json

hdr = {'Content-Type':'application/json'}
def createServer(req):
    url = '${URL}/provisioning/servers'
    print url
    r =requests.post(url, headers=hdr, data=json.dumps(req))
    print r.text
    result = json.loads(r.text)

req = {'zone_id': 'a27c5a9f-c5df-47f0-b1b6-fa0dd4b6c7a5',
        'name':'auto_vm1',
        'request':{
            'server':{
                'name':'auto_vm1',
                'imageRef':'http://10.1.0.1:9292/v2/images/282ae96c-644e-41b6-a206-ef3fd881908b',
                'flavorRef':'http://10.1.0.1:8774/v2/9063caa05aab41cd8e34ef6a115e0915/flavors/4'
                }
        }
    }
createServer(req)
~~~
