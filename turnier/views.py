# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from turnier1.models import Spiel, Turnier, Spielort, Settings


# Da nicht alle Spiele auf die Bildschirmseite passen werde nur du die lezten Ergenisse angezeigt
ANZAHL_ERGEBNISSE_ANZEIGEN = 6 

#+++++++++++++++++++++++++++++++++++++++++++++
# Loesche alle Nones aus toreH und ToreG und ersetyte mit ' '
#+++++++++++++++++++++++++++++++++++++++++++++
def loesche_none(plan):

    for spiel in plan:
            if spiel.toreH == None: 
                spiel.toreH = ' '
            if spiel.toreG == None:
                spiel.toreG = ' '
    return
#+++++++++++++++++++++++++++++++++++++++++++++
# Pruefe ob eine Turnier Spielplan online darf
#+++++++++++++++++++++++++++++++++++++++++++++
def turnier_aktiv():

    q_settings = Settings.objects.all()

    #print q_settings
    # wurde schon ein turnier angelegt
    kein_turnier = True
    if q_settings: # ja turnier vorhanden

        # darf der Spielplan online
        q_settings = Settings.objects.get(pk=1)
        akt_id     = q_settings.online_turnier_id # <>0 plan darf online

        if akt_id != '0':
            kein_turnier = False

    return kein_turnier

#+++++++++++++++++++++++++++++++++++++++++++++
# erzeuge array: [(spiel,hallen_farbe),(spiel,hallen_farbe),....] 
#+++++++++++++++++++++++++++++++++++++++++++++
def array_spiel_hallenfarbe(akt_id, spielplan):

    #--- erzeuge ein array fue jedes spiel die hallenfarbe
    q_hallen = Spielort.objects.filter(turnier=akt_id)
    halle_farbe = []
    for spiel in spielplan:

        for halle in q_hallen:

            if halle.hallen_name == spiel.halle:
                halle_farbe.append(halle.farbe)

    #--- erzeuge array: [(spiel,hallen_farbe),(spiel,hallen_farbe),....]
    spiel_und_farbe = []
    i=0
    for spiel in spielplan:
        spiel_und_farbe.append((spiel,halle_farbe[i]))
        i +=1

    return spiel_und_farbe

#----------------------------------------------------
# Ausgabe der Tabellen
#----------------------------------------------------  
def index(request):

    kein_turnier= turnier_aktiv() # es wird die ID des aktuellen Turnier zurueck gegeben

    # wenn kein Spielplan
    if kein_turnier:    
        return render(request,'turnier/nothing.html')

    q_settings = Settings.objects.get(pk=1)
    akt_id     = q_settings.aktives_turnier_id # ist ein Turnier aktiv


    spielplan = Spiel.objects.filter(turnier=akt_id).order_by('zeit', '-halle') # alle Spiele für das Turnier 
   
    # da nicht alle Spiele angezeigt werden koennen zeige nur die letzten 10 ergebnisse an
    i=0
    for spiel in spielplan:
        if spiel.toreH != None:
            i +=1


    if i > ANZAHL_ERGEBNISSE_ANZEIGEN: # es sind mehr Spiele mit Ergebnissen im Spielplan
        
        n = i - ANZAHL_ERGEBNISSE_ANZEIGEN
        spielplan = Spiel.objects.filter(turnier=akt_id).order_by('zeit', '-halle')[n:]

    #--- nehem aus den feldern toreH und toreG 'None' heraus wenn kein Ergebniss eingetregen
    loesche_none(spielplan)
 

    # erzeuge array: [(spiel,hallen_farbe),(spiel,hallen_farbe),....]
    spiel_und_farbe=array_spiel_hallenfarbe(akt_id, spielplan)

    #--- erzeuge den Spielplan fur die Gruppen
    spielplan_m_g1 = Spiel.objects.filter(turnier=akt_id,spiel_type='Gruppe 1',jugend='m').order_by('zeit', '-halle')
    spielplan_m_g2 = Spiel.objects.filter(turnier=akt_id,spiel_type='Gruppe 2',jugend='m').order_by('zeit', '-halle')
    spielplan_m_g3 = Spiel.objects.filter(turnier=akt_id,spiel_type='Gruppe 3',jugend='m').order_by('zeit', '-halle')
    spielplan_m_g4 = Spiel.objects.filter(turnier=akt_id,spiel_type='Gruppe 4',jugend='m').order_by('zeit', '-halle')

    spielplan_w_g1 = Spiel.objects.filter(turnier=akt_id,spiel_type='Gruppe 1',jugend='w').order_by('zeit', '-halle')
    spielplan_w_g2 = Spiel.objects.filter(turnier=akt_id,spiel_type='Gruppe 2',jugend='w').order_by('zeit', '-halle')
    spielplan_w_g3 = Spiel.objects.filter(turnier=akt_id,spiel_type='Gruppe 3',jugend='w').order_by('zeit', '-halle')
    spielplan_w_g4 = Spiel.objects.filter(turnier=akt_id,spiel_type='Gruppe 4',jugend='w').order_by('zeit', '-halle')

    loesche_none(spielplan_m_g1)
    loesche_none(spielplan_m_g2)
    loesche_none(spielplan_m_g3)
    loesche_none(spielplan_m_g4)
    loesche_none(spielplan_w_g1)
    loesche_none(spielplan_w_g2)
    loesche_none(spielplan_w_g3)
    loesche_none(spielplan_w_g4)

    array_spielplaene_m = []
    if spielplan_m_g1: array_spielplaene_m.append(spielplan_m_g1)
    if spielplan_m_g2: array_spielplaene_m.append(spielplan_m_g2)
    if spielplan_m_g3: array_spielplaene_m.append(spielplan_m_g3)
    if spielplan_m_g4: array_spielplaene_m.append(spielplan_m_g4)

    array_spielplaene_w = []
    if spielplan_w_g1: array_spielplaene_w.append(spielplan_w_g1)
    if spielplan_w_g2: array_spielplaene_w.append(spielplan_w_g2)
    if spielplan_w_g3: array_spielplaene_w.append(spielplan_w_g3)
    if spielplan_w_g4: array_spielplaene_w.append(spielplan_w_g4)
  
    q_turnier            = Turnier.objects.get(pk=akt_id)
    turnier_name         = q_turnier.turnier_name
    turnier_ueberschrift = q_turnier.ueberschrift

    context = RequestContext(request, {
        'spiel_und_farbe'      : spiel_und_farbe,
        'spielplan'            : spielplan,
        'turnier_name'         : turnier_name,
        'turnier_ueberschrift' : turnier_ueberschrift,
        'array_spielplaene_m'  : array_spielplaene_m,
        'array_spielplaene_w'  : array_spielplaene_w,
    })
    return render(request,'turnier/index.html',context)

#----------------------------------------------------
# Ausgabe der ganzen Tabelle ohne Gruppen
#----------------------------------------------------  
def spielplan(request):

    kein_turnier= turnier_aktiv() # es wird die ID des aktuellen Turnier zurueck gegeben
   
    # wenn kein Spielplan
    if kein_turnier:
        return render(request,'turnier/nothing.html')

    q_settings = Settings.objects.get(pk=1)
    akt_id     = q_settings.aktives_turnier_id # ist ein Turnier aktiv
   
    spielplan = Spiel.objects.filter(turnier=akt_id).order_by('zeit', '-halle') # alle Spiele für das Turnier 

    #--- nehem aus den feldern toreH und toreG 'None' heraus wenn kein Ergebniss eingetregen
    loesche_none(spielplan)

    # erzeuge array: [(spiel,hallen_farbe),(spiel,hallen_farbe),....]
    spiel_und_farbe = array_spiel_hallenfarbe(akt_id, spielplan)

    q_turnier            = Turnier.objects.get(pk=akt_id)
    turnier_name         = q_turnier.turnier_name
    turnier_ueberschrift = q_turnier.ueberschrift
    text                 = 'Gesamtspielplan'


    context = RequestContext(request, {
        'text'                 : text,
        'spiel_und_farbe'      : spiel_und_farbe,
        'spielplan'            : spielplan,
        'turnier_name'         : turnier_name,
        'turnier_ueberschrift' : turnier_ueberschrift,
    })
    return render(request,'turnier/t_spielplan.html',context) 

#----------------------------------------------------
# Ausgabe der Tabellen nur weibliche Jugend
#----------------------------------------------------  
def spielpl_weibl(request):

    kein_turnier= turnier_aktiv() # es wird die ID des aktuellen Turnier zurueck gegeben
   
    # wenn kein Spielplan
    if kein_turnier:
        return render(request,'turnier/nothing.html')

    q_settings = Settings.objects.get(pk=1)
    akt_id     = q_settings.aktives_turnier_id # ist ein Turnier aktiv

    spielplan = Spiel.objects.filter(turnier=akt_id,jugend='w').order_by('zeit', '-halle') # alle Spiele für das Turnier 

    #--- nehem aus den feldern toreH und toreG 'None' heraus wenn kein Ergebniss eingetregen
    loesche_none(spielplan)

    # erzeuge array: [(spiel,hallen_farbe),(spiel,hallen_farbe),....]
    spiel_und_farbe = array_spiel_hallenfarbe(akt_id, spielplan)

    q_turnier            = Turnier.objects.get(pk=akt_id)
    turnier_name         = q_turnier.turnier_name
    turnier_ueberschrift = q_turnier.ueberschrift
    text                 = 'Spielplan weibliche Jugend'

    context = RequestContext(request, {
        'text'                 : text,
        'spiel_und_farbe'      : spiel_und_farbe,
        'spielplan'            : spielplan,
        'turnier_name'         : turnier_name,
        'turnier_ueberschrift' : turnier_ueberschrift,
    })
    return render(request,'turnier/t_spielplan.html',context) 

#----------------------------------------------------
# Ausgabe der Tabellen nur maennliche Jugend
#----------------------------------------------------  
def spielplan_maen(request):

    kein_turnier= turnier_aktiv() # es wird die ID des aktuellen Turnier zurueck gegeben
   
    # wenn kein Spielplan
    if kein_turnier:
        return render(request,'turnier/nothing.html')

    q_settings = Settings.objects.get(pk=1)
    akt_id     = q_settings.aktives_turnier_id # ist ein Turnier aktiv

    spielplan = Spiel.objects.filter(turnier=akt_id,jugend='m').order_by('zeit', '-halle') # alle Spiele für das Turnier 

    #--- nehem aus den feldern toreH und toreG 'None' heraus wenn kein Ergebniss eingetregen
    loesche_none(spielplan)

    # erzeuge array: [(spiel,hallen_farbe),(spiel,hallen_farbe),....]
    spiel_und_farbe = array_spiel_hallenfarbe(akt_id, spielplan)

    q_turnier            = Turnier.objects.get(pk=akt_id)
    turnier_name         = q_turnier.turnier_name
    turnier_ueberschrift = q_turnier.ueberschrift
    text                 = 'Spielplan männliche Jugend'

    context = RequestContext(request, {
        'text'                 : text,
        'spiel_und_farbe'      : spiel_und_farbe,
        'spielplan'            : spielplan,
        'turnier_name'         : turnier_name,
        'turnier_ueberschrift' : turnier_ueberschrift,
    })
    return render(request,'turnier/t_spielplan.html',context) 

#------------------------------------------
# Hier wir hingesprungen wenn die Berechtigungen nicht ausreichen
#------------------------------------------
def no_permission(request):


    context = RequestContext(request, {
        'user'        : request.user,

    })
    template = loader.get_template('turnier/no_permission.html')    
    return HttpResponse(template.render(context))



