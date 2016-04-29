import logging
import yaml
from django.conf import settings

PYENGINE_CONF = getattr(settings, 'PYENGINE')

def getGlobalConfig(): 
    conf = loadYAML(PYENGINE_CONF['global'])

    return conf['GLOBAL']

def getRouterConfig(): 
    conf = loadYAML(PYENGINE_CONF['router'])

    return conf['ROUTER']

def getErrorConfig(): 
    conf = loadYAML(PYENGINE_CONF['error'])

    return conf['ERROR']

def getPluginConfig(): 
    conf = loadYAML(PYENGINE_CONF['plugin'])

    return conf['PLUGIN']

def loadYAML(yaml_path, key=None):
    logger = logging.getLogger(__name__)

    try:
        with open(yaml_path, 'r') as f:
            return yaml.load(f)

    except Exception as e:
        logger.error('Load YAML Error: %s' %(e))
        return False
