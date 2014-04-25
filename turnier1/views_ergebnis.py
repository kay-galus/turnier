# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render

from turnier1.models import Spiel, Turnier, Spielort, Settings
from django.contrib.auth.decorators import login_required, permission_required

#----------------------------------------------------
# Ausgabe der Liste aller Turniere
# Auswahl eines Turniers 
# Anzeige der Ergebnisliste des Turniers
#----------------------------------------------------  
def ergebnis_list(request):

    q_alle_turniere = Turnier.objects.order_by('pub_date')
    akt_turnier     = Settings.objects.get(pk=1)

    if request.method == 'POST':

        #alle_turniere = Turnier.objects.all()
        try:
            t_id=request.POST['choice'] # choice aus dem Form holen
        except (KeyError):
            pass
        else:
           
            # wurde ein Turnier markiert
            if int(t_id) > 0:

                q_turnier = Turnier.objects.get(pk=t_id)

                # gebe die Ergenisliste für das Turnier aus
                q_spiele_maen = Spiel.objects.filter(turnier=t_id,jugend='m').order_by('zeit', '-halle')
                q_spiele_weib = Spiel.objects.filter(turnier=t_id,jugend='w').order_by('zeit', '-halle')
                q_spiele_sonst=Spiel.objects.filter(turnier=t_id).exclude(jugend='w').exclude(jugend='m').order_by('jugend','zeit', '-halle')

                context = RequestContext(request, {
                    'turnier_name'    : q_turnier.turnier_name,
                    'spiele_maen'     : q_spiele_maen,
                    'spiele_weib'     : q_spiele_weib,
                    'spiele_sonst'    : q_spiele_sonst,
                })
                return render(request,'turnier1/ergebnis_list.html',context)

 
    context = RequestContext(request, {
        'alle_turniere'     : q_alle_turniere,
    })
    return render(request,'turnier1/ergebnis.html',context)







