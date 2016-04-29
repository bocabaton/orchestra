from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class WorkflowManager(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def registerWorkflow(self, params):

        dao = self.locator.getDAO('workflow') 

        dic = {}
        dic['template']   = params['template']
        dic['template_type']   = params['template_type']

        workflow = dao.insert(dic)

        return self.locator.getInfo('WorkflowInfo', workflow)

    def listWorkflows(self, search, search_or, sort, page):
        dao = self.locator.getDAO('workflow')

        output = []
        (workflows, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)

        for item in workflows:
            info = self.locator.getInfo('WorkflowInfo', item)
            output.append(info)

        return (output, total_count)

    def getWorkflow(self, params):
        dao = self.locator.getDAO('workflow')

        workflows = dao.getVOfromKey(workflow_id=params['workflow_id'])

        if workflows.count() == 0:
            raise ERROR_NOT_FOUND(key='workflow_id', value=params['workflow_id'])

        return self.locator.getInfo('WorkflowInfo', workflows[0])

    def getWorkflowId(self, template, template_type):
        """
        find Workflow ID
        """
        search = [{'key':'template', 'value':template, 'option':'eq'},
                  {'key':'template_type', 'value':template_type, 'option':'eq'}]
        search_or = []
        sort = {}
        page = {}
        (items, count) = self.listWorkflows(search, search_or, sort, page)
        if count == 0:
            raise ERROR_NOT_FOUND(key='template', value=template)
        return items[0].output['workflow_id']

    def deleteWorkflow(self, params):
        dao = self.locator.getDAO('workflow') 

        workflows = dao.getVOfromKey(workflow_id=params['workflow_id'])

        if workflows.count() == 0:
            raise ERROR_NOT_FOUND(key='workflow_id', value=params['workflow_id'])

        workflows.delete()

        return {}

    ##############################################
    # Task map/unmap
    ##############################################
    def mapTask(self, params):
        dao = self.locator.getDAO('task')
       
        item = params['map'] 
        dic = {}
        dic['name'] = item['name']
        # Check Workflow 
        w_dao = self.locator.getDAO('workflow')
        workflows = w_dao.getVOfromKey(workflow_id=params['workflow_id'])
        if workflows.count() == 0:
            raise ERROR_INVALID_PARAMETER(key='workflow_id', value=params['workflow_id'])
        dic['workflow'] = workflows[0]
        dic['task_uri'] = item['task_uri']
        dic['task_type'] = item['task_type']

        task = dao.insert(dic)

        return self.locator.getInfo('TaskInfo', task)

    def listTasks(self, workflow_id):
        dao = self.locator.getDAO('task')
        output = []
        search = [{'key':'workflow_id', 'value':workflow_id, 'option':'eq'}]
        search_or = []
        sort = {}
        page = {}
        (tasks, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)

    def getTaskByName(self, workflow_id, name):
        dao = self.locator.getDAO('task')
        search = [{'key':'workflow_id', 'value':workflow_id, 'option':'eq'},
                  {'key':'name', 'value':name, 'option':'eq'}]
        search_or = []
        sort = {}
        page = {}
        (tasks, total_count)  = dao.select(search=search, search_or=search_or, sort=sort, page=page)

        if tasks.count() == 0:
            raise ERROR_NOT_FOUND(key='name', value=name)

        return self.locator.getInfo('TaskInfo', tasks[0])


