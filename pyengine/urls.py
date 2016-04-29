from django.conf.urls import include, url
from pyengine.lib.request import Request

urlpatterns = [
    url(r'^.*', Request.as_view()),
]
