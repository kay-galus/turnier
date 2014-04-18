from turnier1.models import Spiel, Turnier, Spielort, Settings
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class Prozess_cvm_file(object):

    def __init__(self):
        print 'A new Class'


    def prozess(self, turnier_id):
        print turnier_id
        
        #print akt_turnier
        #return 'frosch'

        akt_turnier = get_object_or_404(Turnier, pk=turnier_id)

        # Lister der angelegten Turnier ausgeben
        context = RequestContext(request, {
            'akt_turnier'   : q_settings.aktives_turnier,
        })
        return render(request,'turnier1/load_file.html',context)
