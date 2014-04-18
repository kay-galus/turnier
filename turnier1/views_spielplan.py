# -*- coding: utf-8 -*-

from django.http import HttpResponse

from django.template import RequestContext, loader
from django.forms.models import inlineformset_factory

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from turnier1.models import Spiel, Turnier, Spielort, Settings
from turnier1.forms import EditSpiel11Form, TurnierAnlegen11Form, EditSpielForm
from django.contrib.auth.decorators import login_required, permission_required

import pusher
#++++++++++++++++++++++++++++++++++++++++
#  Hiermit wird der Trigger fuer den 
#  Seitenupdate der Homeseite ausgeloest
#  Ueber den Dienst: puscher.com
#++++++++++++++++++++++++++++++++++++++++
def trigger_site_update():

    p = pusher.Pusher(
                    app_id='69986',
                    key='078584de032a0d8616b3',
                    secret='ccdf5c6c3f044092a6a5'
                        )
    try:
        p['turnier_channel'].trigger('update_site', {'message': 'hello world'})
    except:
        return
    else:
        return
#----------------------------------------------------
# Spielplan ausgeben
#
#----------------------------------------------------  
@login_required
@permission_required('turnier1.spiele_admin',login_url='/nopermission/')
def spielplan(request):

    q_settings = Settings.objects.get(pk=1)
    akt_id     = q_settings.aktives_turnier_id # ist ein Turnier aktiv

    if akt_id != '0':
        turnier_aktiv = True
        spielplan     = Spiel.objects.filter(turnier=akt_id).order_by('zeit', '-halle') # alle Spiele für das Turnier
        q_turnier     = Turnier.objects.get(pk=akt_id)
        turnier       = q_settings.aktives_turnier
        ueberschrift  = q_turnier.ueberschrift
    else:
        turnier_aktiv = False
        spielplan     = ''
        turnier       = ''
        ueberschrift  = 'Keine Turnier aktiv!'

    context = RequestContext(request, {
        'turnier_aktiv' : turnier_aktiv,
        'turnier'       : turnier,
        'spielplan'     : spielplan,
        'ueberschrift'  : ueberschrift,
    })
    return render(request,'turnier1/spielplan.html',context)

#----------------------------------------------------
# Ein Spiel editieren
# 
#----------------------------------------------------  
@login_required
@permission_required('turnier1.spiele_admin',login_url='/nopermission/')
def spielplan_edit_spiel(request, spiel_id):

    q_settings   = Settings.objects.get(pk=1)     # Querry auf settings
    akt_id       = q_settings.aktives_turnier_id  # ID aktives Turnier
    q_turnier    = Turnier.objects.get(pk=akt_id) # Querry auf Turnier
    turnier      = Turnier.objects.get(pk=akt_id) # Aktives Turnier
    ueberschrift = q_turnier.ueberschrift         # Überschrift aktives Turnier

    q_akt_spiel  = get_object_or_404(Spiel, pk=spiel_id) # aktuelles Spiel
    form_spiel   = EditSpielForm(instance=q_akt_spiel)   # Form mit data des aktuelen Spiels

    if request.method == 'POST':

        q_akt_spiel  = get_object_or_404(Spiel, pk=spiel_id)
        form_spiel = EditSpielForm(request.POST,instance=q_akt_spiel) # Daten des Forms (forms.py) einlesen

        if form_spiel.is_valid(): # sind alle Felde richtig eingegeben

            # Daten aus dem Form auslesen und auf DB Schreiben
            new_store  = form_spiel.save()

            # Trigger fuer pusher.com ausloesen
            trigger_site_update()

            return HttpResponseRedirect('/turnier/spielplan/') # Ruecksprung

    context = RequestContext(request, {
        'spiel_id'     : spiel_id,
        'form_spiel'   : form_spiel,
        'turnier'      : turnier,
        'ueberschrift' : ueberschrift,
    })
    return render(request,'turnier1/spielplan_edit.html',context)
     
#---------------------------------------------
# Ein Spiel löschen
#
#----------------------------------------------
@login_required
@permission_required('turnier1.spiele_admin',login_url='/nopermission/')
def spielplan_del_spiel(request, spiel_id):

    q_settings = Settings.objects.get(pk=1)    # Querry auf settings
    akt_id     = q_settings.aktives_turnier_id # ID aktives Turnier
    q_turnier  = Turnier.objects.get(pk=akt_id) # Querry auf Turnier
    turnier    = Turnier.objects.get(pk=akt_id)
    ueberschrift  = q_turnier.ueberschrift

    if request.method == 'POST':

        q_akt_spiel  = get_object_or_404(Spiel, pk=spiel_id)
        try:
            t_id=request.POST['delete'] # choice aus dem Form holen
        except (KeyError):
            pass
        else:
            if t_id == 'delete':      
                q_akt_spiel.delete() # Spiel löschen

                # Trigger fuer pusher.com ausloesen
                trigger_site_update()

        return HttpResponseRedirect('/turnier/spielplan/') # Ruecksprung
    
    q_akt_spiel  = get_object_or_404(Spiel, pk=spiel_id)

    context = RequestContext(request, {
        'spiel_id'   : spiel_id,
        'turnier'       : turnier,
        'spiel_data'    : q_akt_spiel,
        'ueberschrift'  : ueberschrift,
    })
    return render(request,'turnier1/spielplan_del.html',context)
#---------------------------------------------
# Neue Spiele eintragen
#
#----------------------------------------------
@login_required
@permission_required('turnier1.spiele_admin',login_url='/nopermission/')
def spielplan_add_spiel(request):

    q_settings   = Settings.objects.get(pk=1)    # Querry auf settings
    akt_id       = q_settings.aktives_turnier_id # ID aktives Turnier
    q_turnier    = Turnier.objects.get(pk=akt_id) # Querry auf Turnier

    form_turnier = TurnierAnlegen11Form(instance=q_turnier)
    spielFormSet = inlineformset_factory(Turnier, Spiel, form=EditSpiel11Form, extra=4,can_delete=True)   
    form_spiel   = spielFormSet()

    if request.method == 'POST':
        
        #form_turnier = TurnierAnlegen11Form(request.POST)
        form_turnier = TurnierAnlegen11Form(request.POST,instance=q_turnier) # Daten des Forms (forms.py) einlesen

        if form_turnier.is_valid(): # sind alle Felde richtig eingegeben

            new_store  = form_turnier.save() # inhalt des forms speichern
            form_spiel = spielFormSet(request.POST, request.FILES, instance=new_store)

            if form_spiel.is_valid():
                form_spiel.save()

                # Trigger fuer pusher.com ausloesen
                trigger_site_update()

                return HttpResponseRedirect('/turnier/spielplan/') # Ruecksprung

    context = RequestContext(request, {
        'form_spiel'   : form_spiel,
        'form_turnier' : form_turnier,
        'turnier'       : q_turnier.turnier_name,
        'ueberschrift'  : q_turnier.ueberschrift,
    })
    return render(request,'turnier1/spielplan_add.html',context)






