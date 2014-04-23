# -*- coding: utf-8 -*-

from django.http import HttpResponse

from django.template import RequestContext, loader
from django.forms.models import inlineformset_factory

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from turnier1.models import Spiel, Turnier, Spielort, Settings
from turnier1.forms import EingabeHallenForm
from django.contrib.auth.decorators import login_required, permission_required

import pusher

ANZAHL_ERGEBNISSE_ANZEIGEN_EINGABE = 3

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
# Ausgabe 1. Seite für Ergenisseingabe
# Spielplan übersicht
# Links zu den Halleneigaben
#----------------------------------------------------  
@login_required
@permission_required('turnier1.spiele_eingeben',login_url='/nopermission/')
def eingabe_gesamtspielplan(request):

    q_settings = Settings.objects.get(pk=1)
    akt_id     = q_settings.aktives_turnier_id # ist ein Turnier aktiv

    if akt_id != '0':
        turnier_aktiv = True
        alle_hallen   = Spielort.objects.filter(turnier=akt_id) # hole alle Hallen für das Turnier
        spielplan     = Spiel.objects.filter(turnier=akt_id).order_by('zeit', '-halle') # alle Spiele für das Turnier
        q_turnier     = Turnier.objects.get(pk=akt_id)
        turnier       = q_settings.aktives_turnier
        ueberschrift  = q_turnier.ueberschrift
    else:
        turnier_aktiv = False
        alle_hallen   = ''
        spielplan     = ''
        turnier       = ''
        ueberschrift  = 'Keine Turnier aktiv!'

    context = RequestContext(request, {
        'turnier_aktiv' : turnier_aktiv,
        'turnier'       : turnier,
        'spielplan'     : spielplan,
        'ueberschrift'  : ueberschrift,
        'alle_hallen'   : alle_hallen,
    })
    return render(request,'turnier1/eingabe.html',context)

#----------------------------------------------------
# Ergebnisseingabe für die Hallen
# 
#----------------------------------------------------  
@login_required
@permission_required('turnier1.spiele_eingeben',login_url='/nopermission/')
def eingabe_halle_spielliste(request, hallen_id):

    q_halle    = Spielort.objects.get(pk=int(hallen_id)) # hole ausgewaehlte Halle
    q_settings = Settings.objects.get(pk=1)
    akt_id     = q_settings.aktives_turnier_id # ist ein Turnier aktiv

    if akt_id != '0':
        turnier_aktiv      = True

        # nur die letzten 4 Ergebnisse anzeigen, dann muss nicht gescrollt werden
        hallen_spielplan   = Spiel.objects.filter(turnier=akt_id, halle=q_halle.hallen_name).order_by('zeit')
        i=0
        for spiel in hallen_spielplan:
            if spiel.toreH != None:
                i +=1

        if i > ANZAHL_ERGEBNISSE_ANZEIGEN_EINGABE: # es sind mehr Spiele mit Ergebnissen im Spielplan
            n = i - ANZAHL_ERGEBNISSE_ANZEIGEN_EINGABE
            hallen_spielplan = Spiel.objects.filter(turnier=akt_id, halle=q_halle.hallen_name).order_by('zeit')[n:]

        q_turnier          = Turnier.objects.get(pk=akt_id)
        turnier            = q_settings.aktives_turnier
        ueberschrift       = q_turnier.ueberschrift

    else:
        turnier_aktiv      = False
        hallen_spielplan   = ''
        turnier            = ''
        ueberschrift       = 'Keine Turnier aktiv!'
        form_eingabe_halle = ''

    context = RequestContext(request, {
        'turnier_aktiv'   : turnier_aktiv,
        'hallen_spielplan': hallen_spielplan,
        'turnier'         : turnier,
        'ueberschrift'    : ueberschrift,
        'hallen_name'     : q_halle.hallen_name,
        'hallen_id'       : hallen_id,
    })
    return render(request,'turnier1/eingabe_spielliste.html',context)
#--------------------------------------------------
# Spielergebniss eintragen
#--------------------------------------------------
@login_required
@permission_required('turnier1.spiele_eingeben',login_url='/nopermission/')
def eingabe_edit_spiel(request, spiel_id):
    
    hallen_id = request.GET.get('id','') # die hallen_id wurde in der URL als Paramter übergeben

    q_akt_spiel   = get_object_or_404(Spiel, pk=spiel_id)
    form_eingabe  = EingabeHallenForm(instance=q_akt_spiel)
    

    if request.method == 'POST':
        
        form_eingabe = EingabeHallenForm(request.POST,instance=q_akt_spiel) # Daten des Forms (forms.py) einlesen

        if form_eingabe.is_valid(): # sind alle Felde richtig eingegeben

            # Daten aus dem Form auslesen und auf DB Schreiben
            new_store  = form_eingabe.save()

            # Trigger fuer pusher.com ausloesen
            trigger_site_update()
            
            
            r = '/turnier/eingabe/'+ hallen_id
            return HttpResponseRedirect(r) # Ruecksprung

    q_akt_spiel  = get_object_or_404(Spiel, pk=spiel_id)

    context = RequestContext(request, {
        'spiel_zeit'   : q_akt_spiel.zeit,
        'halle'        : q_akt_spiel.halle,
        'jugend'       : q_akt_spiel.jugend,
        'heim'         : q_akt_spiel.heim,
        'gast'         : q_akt_spiel.gast,
        'toreH'        : q_akt_spiel.toreH,
        'toreG'        : q_akt_spiel.toreG,        
        'hallen_id'    : hallen_id,
        'spiel_id'     : spiel_id,
        'form_eingabe' : form_eingabe,
    })
    return render(request,'turnier1/eingabe_edit.html',context)





