from pyengine.lib import config

class ERROR(Exception):
    def __init__(self, err_obj):
        self.err_obj = err_obj
        self.status_code = err_obj['status_code']

        self.message = {}
        self.message['code'] = err_obj['class']
        self.message['message'] = err_obj['message']
        self.message['args'] = {}

    def __add__(self, key, value):
        key = str(key)
        if type(unicode()) == type(value):
            value = value.encode('utf-8')
        else:
            value = str(value)

        if any(key == k for k in self.err_obj['args']):
            self.message['message'] = self.message['message'].replace("%"+key, value)
            self.message['args'][key] = value

    def __str__(self):
        return repr(self.message)

def init(self, **keywords):
    ERROR.__init__(self, self.err_obj)

    for key in keywords.keys():
        self.__add__(key, keywords[key])

def createError(err_obj):
    class_name = err_obj['class']
    exec("globals()['%s'] = type('%s', (ERROR,), {'__init__': init, 'err_obj':err_obj})" %(class_name, class_name))


# Create Error Classes
for err_obj in config.getErrorConfig():
	createError(err_obj)
