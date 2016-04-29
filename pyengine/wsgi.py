import os, sys
path = os.path.abspath(__file__ + '/../..')
if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyengine.settings")

application = get_wsgi_application()
