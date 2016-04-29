# Create Region

# Environment

Keyword | Value | Description
----    | ----  | ----
URL     | http://127.0.0.1/api/v1 | URL for request
METADATA      | http://127.0.0.1/api/v1/catalog/{stack_id}/env
ZONE_ID | 14b14664-705e-42e9-8106-240b83f9df79
NUM_NODES   | 3

# Create Server

~~~python
import requests
import json

hdr = {'Content-Type':'application/json'}
def createServer(req):
    url = '${URL}/provisioning/servers'
    try:
        r =requests.post(url, headers=hdr, data=json.dumps(req))
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

body = {'add':{'cluster':cluster}}
addEnv('${METADATA}', body)

~~~
