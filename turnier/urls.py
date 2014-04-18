from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
   
    url(r'^$',              'turnier.views.spielplan', name='spielplan'),
    url(r'^anzeige1$',      'turnier.views.index', name='index'),
    url(r'^spielplweibl/$', 'turnier.views.spielpl_weibl', name='spielpl_weibl'),
    url(r'^spielplanmaen/$','turnier.views.spielplan_maen', name='spielplan_maen'),
    url(r'^nopermission/$', 'turnier.views.no_permission', name='no_permission'),

    url(r'^turnier/', include('turnier1.urls',namespace="turnier1")),
    url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.backends.default.urls')),

)
