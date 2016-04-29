# Unitest

## Environment

Keyword | Value
----    | ----
URL     | http://127.0.0.1/api/v1

## Portfolio

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


url = '${URL}/catalog/portfolios'
display('List Portfolios')
show(makeGet(url, header))

display('Create Portfolio')
body = {'name':'Data Solution', 'description':'Data Solution, RDBMS, NoSQL, NewSQL',
        'owner':'choonho.son'}
portfolio = makePost(url, header, body)
show(portfolio)
p_id = portfolio['portfolio_id']
url = '${URL}/catalog/portfolios/%s' % p_id

display('Update Portfolio')
body = {'name':'Database Solution'}
show(makePut(url, header, body))

display('Get Portfolio')
portfolio = makeGet(url, header)
show(portfolio)

######################################
# Product
######################################
product_url = '${URL}/catalog/products'
display('List Product')
show(makeGet(product_url, header))

display('Create Product')
body = {'portfolio_id':p_id, 'name':'Couchbase', 'short_description':'Couchbase NoSQL',
        'description':'Couchbase NoSQL Enterprise', 'provided_by':'Couchbase (c)',
        'vendor':'Couchbase LTD'}
product = makePost(product_url, header, body)
show(product)
product_id = product['product_id']
product_url2 = '${URL}/catalog/products/%s' % product_id

display('Update Product')
body = {'provided_by':'PyEngine Group'}
show(makePut(product_url2, header, body))

display('Get Product')
show(makeGet(product_url2, header))

######################################
# Product Detail
######################################
detail_url = '${URL}/catalog/products/%s/detail' % product_id
display('Create Product detail')
body = {'email':'test@test.com', 'support_link':'http://help.test.com','support_description':'Can I help you?'}
show(makePost(detail_url, header, body))

display('Get Product detail')
show(makeGet(detail_url, header))

######################################
# Package
######################################
package_url = '${URL}/catalog/packages'
body = {'product_id':product_id, 'pkg_type':'bpmn', 'template':'http://127.0.0.1/static/database/couchbase/couchbase.bpmn', 'version':'4.5'}
display('Create Package')
package = makePost(package_url, header, body)
package_id = package['package_id']
show(package)

package_url2 = '${URL}/catalog/packages/%s' % package_id
display('List Package')
show(makeGet(package_url2, header))

display('Update Package')
body = {'description':'Beta 1'}
show(makePut(package_url2, header, body))


######################################
# Tag
######################################
tag_url = '${URL}/catalog/products/%s/tags' % product_id
display('Create Tag')
body = {'create':{'key':'k1', 'value':'v1'}}
tag = makePost(tag_url, header, body)
tag_id = tag['uuid']
show(tag)

display('Update Tag')
body = {'update':{'uuid':tag_id, 'key':'new K1', 'value':'new V1'}}
show(makePost(tag_url, header, body))

display('List Tag')
body = {'list':[]}
show(makePost(tag_url, header, body))

display('Delete Tag')
body = {'delete':tag_id}
show(makePost(tag_url, header, body))

######################################
# Register Workflow
######################################
display('Register Workflow')
workflow_url = '${URL}/catalog/workflows'
body = {'template':'http://127.0.0.1/static/database/couchbase/couchbase.bpmn', 'template_type':'bpmn'}
workflow = makePost(workflow_url, header, body)
workflow_id = workflow['workflow_id']
show(workflow)

######################################
# Map Task
######################################
display('Map Task #1')
task_url = '${URL}/catalog/workflows/%s/tasks' % workflow_id
body = {'map': {'name':'Deploy VMs', 'task_type':'jeju', 'task_uri':'http://127.0.0.1/static/database/couchbase/infra.md'}}
task = makePost(task_url, header, body)
task_id = task['task_id']
show(task)

display('Map Task #2')
task_url = '${URL}/catalog/workflows/%s/tasks' % workflow_id
body = {'map': {'name':'Install Jeju', 'task_type':'ssh+cluster', 'task_uri':"apt-get update;apt-get -y install python-pip;pip install jeju --upgrade"}}
task = makePost(task_url, header, body)
task_id = task['task_id']
show(task)

display('Map Task #3')
task_url = '${URL}/catalog/workflows/%s/tasks' % workflow_id
body = {'map': {'name':'Install Couchbase Package', 'task_type':'ssh+cluster', 'task_uri':'env > /root/test'}}
task = makePost(task_url, header, body)
task_id = task['task_id']
show(task)



######################################
# Get Task
######################################
display('Get Task by Name')
body = {'get': 'Deploy VMs'}
show(makePost(task_url, header, body))

body = {'get': 'Install Jeju'}
show(makePost(task_url, header, body))

body = {'get': 'Install Couchbase Package'}
show(makePost(task_url, header, body))



######################################
# Deploy Stack
######################################
display('Select Zone for deploy')
zone_url = '${URL}/provisioning/zones'
zones = makeGet(zone_url, header)
zone_id = zones['results'][0]['zone_id']
show(zones)

stack_url = '${URL}/catalog/stacks'
display('Deploy Stack')
body = {'package_id':package_id, 'env': {'jeju':{'NUM_NODES':2,'ZONE_ID':zone_id}}}
stack = makePost(stack_url, header, body)
stack_id = stack['stack_id']
show(stack)
stack_id = stack['stack_id']

display('Add Stack env')
stack_url2= '${URL}/catalog/stacks/%s/env' % stack_id
body = {'add': {'test':'http://127.0.0.1'}}
stack = makePost(stack_url2, header, body)
show(stack)

body = {'add': {'vm':[{'vm1':'1.2.3.4'},{'vm2':'2.2.2.2'}]}}
stack = makePost(stack_url2, header, body)
show(stack)

display('Get Stack env')
body = {'get':'cluster'}
kv = makePost(stack_url2, header, body)
show(kv)

######################################
# Recursive Delete
######################################
#display('Delete Tag')
#show(makeDelete(tag_url, header))

display('Delete Package')
show(makeDelete(package_url2, header))

display('Delete Product detail')
show(makeDelete(detail_url, header))

display('Delete Product')
show(makeDelete(product_url2, header))

display('Delete Portfolio:%s' % p_id)
portfolio = makeDelete(url, header)
show(portfolio)
~~~
