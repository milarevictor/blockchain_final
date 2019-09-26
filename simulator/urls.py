from django.urls import path
from django.conf.urls import url
from simulator import views
from .views import start_simul, get_log, create_simul, save_blockchain


urlpatterns = [
    # url(r'^$', start_simul, name='start-simul'),
    url(r'^$', start_simul, name='start-simul'),
    url(r'^createSimul$', create_simul, name='create-simul'),
    url(r'^api/log/$', get_log, name='get-log'),
    url(r'^api/save/$', save_blockchain, name='save-blockchain')

]
