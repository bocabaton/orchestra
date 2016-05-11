import json
import requests
import uuid
import os

from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

from io import BytesIO

from SpiffWorkflow import Task
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.util import *
from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.bpmn.specs.UserTask import UserTask
from SpiffWorkflow.bpmn.storage.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.storage.CompactWorkflowSerializer import CompactWorkflowSerializer
from SpiffWorkflow.bpmn.storage.Packager import Packager

from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow.specs.Simple import Simple

import logging
LOG = logging.getLogger(__name__)

class PyengineBpmnWorkflow(BpmnWorkflow):
    def __init__(self, workflow_spec, workflow_id, stack_id, **kwargs):
        """
        constructor
        """
        super(PyengineBpmnWorkflow, self).__init__(workflow_spec, name=workflow_id, script_engine=None, read_only=False, **kwargs)
        self.stack_id = stack_id
        self.workflow_id = workflow_id

class ServiceTask(Simple, BpmnSpecMixin, Manager):
    """
    Task Spec for a bpmn:serviceTask node.
    """
    def is_engine_task(self):
        return False

    def entering_ready_state(self, task):
        print "Do ready : %s" % task.get_description()
        stack_id = task.workflow.stack_id
        p_mgr = self.locator.getManager('PackageManager')
        state = {'workflow_state':{task.get_description():'building'}}
        p_mgr.addEnv2(stack_id, state)

    def entering_complete_state(self, task):
        LOG.debug('### workflow_id:%s' % task.workflow.name)
        LOG.debug('### stack_id:%s' % task.workflow.stack_id)
        # TODO: find exact url
        url = 'http://127.0.0.1/api/v1/catalog/workflows/%s/tasks' % task.workflow.name
        meta_url = 'http://127.0.0.1/api/v1/catalog/stacks/%s/env' % task.workflow.stack_id
        workflow_id = task.workflow.name
        stack_id = task.workflow.stack_id
        mgr = self.locator.getManager('WorkflowManager')
        task_info = mgr.getTaskByName(workflow_id, task.get_description())
        self.logger.debug(task_info)
        ttype = task_info.output['task_type']
        self.logger.debug("Task type:%s" % ttype)
        (cmd_type, group) = self._parseTaskType(ttype)
        if group == 'localhost' and cmd_type == 'jeju':
            # every jeju has 'METADATA' keyword for metadata put/get
            kv = "METADATA=%s," % meta_url
            # Add Global Env
            kv = self._getKV(stack_id, 'jeju', kv)
            if kv[-1] == ",":
                kv = kv[:-1]
            cmd = 'jeju -m %s -k %s' % (task_info.output['task_uri'], kv)
            LOG.debug('### cmd:%s' % cmd) 
            os.system(cmd)

        else:
            group_info = self._getKV2(stack_id, group)
            mgr = self.locator.getManager('CloudManager')
            for server_id in group_info:
                self.logger.debug("Execute@(%s)" % server_id)
                if cmd_type == 'jeju':
                    kv = 'METADATA=%s,' % meta_url
                    # Add Global Env
                    kv = self._getKV(stack_id, 'jeju', kv)
                    # Add Local Env
                    kv = self._getKV(stack_id, server_id, kv)
                    # Filter last character
                    if kv[-1]==",":
                        kv = kv[:-1]
                    cmd = 'jeju -m %s -k %s 2>&1 /tmp/jeju.log' % (task_info.output['task_uri'], kv)
                elif cmd_type == 'ssh':
                    cmd = task_info.output['task_uri']
                params = {'server_id':server_id, 'cmd':cmd}
                output = mgr.executeCmd(params) 
                self.logger.debug('cmd output:%s' % output)
                #server_info = mgr.getServerInfo(server_id)
                #if server_info.has_key['floatingip'] == True:
                #    self.logger.debug("Access by floatingip (%s)" % server_info['floatingip'])
        # Update State
        state = {'workflow_state':{task.get_description():'complete'}}
        self.logger.debug("Update State to complete:%s" % state)
        p_mgr = self.locator.getManager('PackageManager')
        p_mgr.addEnv2(stack_id, state)

    def _parseTaskType(self, ttype):
        """
        @params:
            - ttask: task type string (cmd type + node group)
                ex) jeju, jeju+cluster, ssh+node1 ...
        @return: (cmd type, node group)
        """
        items = ttype.split("+")
        if len(items) == 2:
            nodes = items[1]
        else:
            nodes = 'localhost'
        return (items[0] , nodes)

    def _getNodeGroup(self, stack_id, group_name):
        """
        @return: list of server information for ssh connection 
                [{'name':'xxxx','ipv4':'xxxx','floatingip':'xxxx','id':'root','pw':'123456'},
                }
        """
        group_list = self._getKV2(stack_id, group_name)
        if group_list == None:
            # Error
            pass
        mgr = self.locator.getManager('CloudManager')
        infos = []
        for server_id in group_list:
            server_info = mgr.getServerInfo(server_id)
            infos.append(server_info)
        return infos
        
    def _getKV(self, stack_id, key, output):
        """
        @params:
            - stack_id: stack_id
            - key: key for get item
            - output: return string

        get Jeju environment
        @return: string for jeju environment
         ex) "NUM_NODES=3,KV=http://1.2.3.4"
        """
        items = self._getKV2(stack_id, key)
        #TODO: items are dictionary
        for key in items.keys():
            value = items[key]
            output = output + "%s=%s," % (key, value)
        return output

    def _getKV2(self, stack_id, key):
        """
        @params:
            - stack_id: stack_id
            - key: key for get item
        @ return: value
        """
        mgr = self.locator.getManager('PackageManager')
        return mgr.getEnv2(stack_id, key)

class ServiceTaskParser(TaskParser):
    pass


class CloudBpmnParser(BpmnParser):
    OVERRIDE_PARSER_CLASSES = {
        full_tag('serviceTask') :   (ServiceTaskParser, ServiceTask),
    }


class InMemoryPackager(Packager):
    PARSER_CLASS = CloudBpmnParser

    @classmethod
    def package_in_memory(cls, workflow_name, workflow_files, editor='signavio'):
        s = BytesIO()
        p = cls(s, workflow_name, meta_data=[], editor=editor)
        p.add_bpmn_files_by_glob(workflow_files)
        p.create_package()
        return s.getvalue()

class Node(object):
    """
    Keep the Task information
    """
    def __init__(self, task):
        self.input = {}
        self.output = {}
        self.task = None
        self.task_type = None
        self.task_name = None
        self.description = None
        self.activity = None
        self.init_task(task)

    def init_task(self, task):
        self.task = task
        self.task_type = task.task_spec.__class__.__name__
        self.task_name = task.get_name()
        self.description = task.get_description()
        self.activity = getattr(task.task_spec, 'service_class', '')

    def show(self):
        print "task type:%s" % self.task_type
        print "task name:%s" % self.task_name
        print "description:%s" % self.description
        print "activity :%s" % self.activity
        print "state name:%s" % self.task.get_state_name()
        print "\n"

class BpmnDriver(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def set_up(self, path, name, workflow_id, stack_id):
        self.spec = self.load_spec(path, name)
        self.workflow = PyengineBpmnWorkflow(self.spec, workflow_id=workflow_id, stack_id=stack_id)
        #self.run_engine()

    def create_workflow(self):
        self.workflow_spec = self.load_workflow_spec()

    def load_spec(self, content_path, workflow_name):
        return self.load_workflow_spec(content_path, workflow_name)

    def load_workflow_spec(self, content_path, workflow_name):
        package = InMemoryPackager.package_in_memory(workflow_name, content_path)
        return BpmnSerializer().deserialize_workflow_spec(package)

    def run_engine(self):
        while 1:
            tasks = self.workflow.get_tasks(state=Task.READY)
            print len(tasks)
            if len(tasks) == 0:
                break
            for task in tasks:
                current_node = Node(task)
                current_node.show()
                self.workflow.complete_task_from_id(task.id)

            self.workflow.do_engine_steps()

    def run(self, template, env, stack_id):
        """
        @params:
            -template:
            -env:
            -stack_id:
        """
        # 1. Load content
        self.env = env
        job = self._loadURI(template)
        self.logger.debug("JOB:\n%s" % job)
        # Save as working directory
        new_path = self._saveTemp(job)
        # Get workflow_id
        w_mgr = self.locator.getManager('WorkflowManager')
        workflow_id  = w_mgr.getWorkflowId(template, template_type = 'bpmn') 
        self.logger.debug("### Workflow ID:%s" % workflow_id)

        # TODO: update name from server
        wf_name = 'Process_1'
        self.set_up(new_path, wf_name, workflow_id, stack_id)

        # 2. Run BPMN
        self.run_engine()

        # 3. Update Stack state
        p_mgr = self.locator.getManager('PackageManager')
        p_mgr.updateStackState(stack_id, "running")
   
    def _loadURI(self, uri):
        """
        @param:
            - uri
        @return:
            - content

        load content from uri
        """
        r = requests.get(uri)
        if r.status_code == 200:
            return r.text
        raise ERROR_NOT_FOUND(key='template', value=uri)

    def _saveTemp(self, content):
        """
        @param:
            - content
        @return:
            - saved file path
        """
        SAVE_DIR = '/tmp'
        new_path = '%s/%s' % (SAVE_DIR, uuid.uuid4())
        fp = open(new_path, 'w')
        fp.write(content)
        fp.close()
        return new_path
