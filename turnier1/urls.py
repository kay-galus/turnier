# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from turnier1 import views
from turnier1 import views_eingabe, views_spielplan

urlpatterns = patterns('',


    # Anzeige gesamtspielplan
    url(r'^$', views.index, name='index'),

    # Spielplanpflege
    url(r'^spielplan/add/$', views_spielplan.spielplan_add_spiel, name='spielplan_add_spiel'),
    url(r'^spielplan/edit/(?P<spiel_id>\d+)$', views_spielplan.spielplan_edit_spiel, name='spielplan_edit_spiel'),
    url(r'^spielplan/delete/(?P<spiel_id>\d+)$', views_spielplan.spielplan_del_spiel, name='spielplan_del_spiel'),
    url(r'^spielplan/$', views_spielplan.spielplan, name='spielplan'),

    # Ergeniseingabe in den Hallen
    url(r'^eingabe/$', views_eingabe.eingabe_gesamtspielplan, name='eingabe_gesamtspielplan'),
    url(r'^eingabe/edit/(?P<spiel_id>\d+)$', views_eingabe.eingabe_edit_spiel, name='eingabe_edit_spiel'),
    url(r'^eingabe/(?P<hallen_id>\d+)$', views_eingabe.eingabe_halle_spielliste, name='eingabe_halle_spielliste'),

    # Turnierpflege
    url(r'^edit/load/$', views.turnier_load, name='turnier_load'), 
    url(r'^edit/load/(?P<turnier_id>\d+)$', views.turnier_load_file, name='turnier_load_file'),
    url(r'^edit/$', views.turniere, name='turniere'),
    url(r'^edit/create/$', views.turnier_create, name='turnier_create'), 
    url(r'^edit/(?P<turnier_id>\d+)$', views.turnier_edit, name='turnier_edit'),  # Turnier edit
  
    # Turnier aktivieren
    url(r'^aktivate/$', views.aktiviate_turnier, name='aktiviate_turnier'),    
    url(r'^aktivate/confirm/(?P<turnier_id>\d+)$', views.aktiviate_turnier_confirm, name='aktiviate_turnier_confirm'), 

)
 