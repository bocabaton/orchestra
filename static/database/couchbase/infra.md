# Create Region

# Environment

Keyword | Value | Description
----    | ----  | ----
URL     | http://127.0.0.1/api/v1 | URL for request
TOKEN   | my_token
METADATA      | http://127.0.0.1/api/v1/catalog/{stack_id}/env
ZONE_ID | 14b14664-705e-42e9-8106-240b83f9df79
NUM_NODES   | 3

# Create Server

~~~python
import requests
import json

hdr = {'Content-Type':'application/json','X-Auth-Token':'${TOKEN}'}
def createServer(req):
    url = '${URL}/provisioning/servers'
    try:
        r =requests.post(url, headers=hdr, data=json.dumps(req))
        if (r.status_code == 200):
            result = json.loads(r.text)
            return result
    except requests.exception.ConnectionError:
        print "Failed to connect"

def getServerDetail(server_id, key):
    url = '${URL}/provisioning/servers/%s/detail' % server_id
    req = {'get':key}
    try:
        r = requests.post(url, headers=hdr, data=json.dumps(req))
        if (r.status_code == 200):
            result = json.loads(r.text)
            return result
    except requests.exception.ConnectionError:
        print "Failed to connect"

def addEnv(url, body):
    r = requests.post(url, headers=hdr, data=json.dumps(body))
    if r.status_code == 200:
        result = json.loads(r.text)

cluster = []
init = []
other = []
addresses = []
for i in range(${NUM_NODES}):
    node_name = "couchbase-%.2d" % (i+1)
    req = {'zone_id': '${ZONE_ID}', 
            'name':node_name,
            'floatingIP':True,
            'request':{
                'server':{
                    'name':node_name,
                    'imageRef':'http://10.1.0.1:9292/v2/images/282ae96c-644e-41b6-a206-ef3fd881908b',
                    'flavorRef':'http://10.1.0.1:8774/v2/9063caa05aab41cd8e34ef6a115e0915/flavors/4'
                    }
            }
        }
    server = createServer(req)
    print server
    cluster.append(server['server_id'])
    if i == 0:
        init.append(server['server_id'])
    else:
        other.append(server['server_id'])
        addr = getServerDetail(server['server_id'],'private_ip_address')
        print addr
        addresses.append(addr['private_ip_address'])

body = {'add':{'cluster':cluster}}
addEnv('${METADATA}', body)

body = {'add':{'init':init}}
addEnv('${METADATA}', body)

body = {'add':{'other':other}}
addEnv('${METADATA}', body)

print "Address format : x.x.x.x:y.y.y.y:d.d.d.d:..."
print addresses
temp = ""
for addr in addresses:
    temp = temp + addr + ":"
print temp

body = {'add':{init[0]:{'ADDED_NODES':temp[:-1]}}}
print body
addEnv('${METADATA}', body)
~~~
