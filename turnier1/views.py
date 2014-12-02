# -*- coding: utf-8 -*-

from django.http import HttpResponse
#from django.http import HttpRequest
from django.template import RequestContext, loader
from django.forms.models import inlineformset_factory

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from turnier1.models import Spiel, Turnier, Spielort, Settings
from turnier1.forms import TurnierAnlegenForm, UploadFileForm, SpielorteForm
from prozess_file import Prozess_cvm_file
from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

import csv
import codecs

DEFAULT_STR_KEIN_TURNIER_AKTIV    = 'Kein Turnier aktiv!'
DEFAULT_STR_KEIN_SPIELPLAN_ONLINE = 'Kein Spielplan online'

#++++++++++++++++++++++++++++++++++++++++++
# Try encoding - output is a UTF-8 File
# input could be a UTF-8, Windows-1252 or ISO-8859-1 file
# Returns a Unicode object on success
#++++++++++++++++++++++++++++++++++++++++++
def try_utf8(data):
    # is it a UTF-8 file?
    try:
        aa = data.decode('utf-8')
    except:
        #print 'not UTF-8'
        pass
    else:
        #print 'was UTF-8' 
        #print data       
        return data # input file return

    try: 
        aa=data.decode('Windows-1252')
    except:
        #print 'not Windows-1252'
        pass
    else:
        bb=aa.encode('utf-8')
        #print bb
        #print 'was Windows-1252'
        return bb

    try:
        aa = data.decode('ISO-8859-1')
    except:
        #print 'not ISO-8859-1'
        pass
    else:
        bb = aa.encode('utf-8')
        #print 'was ISO-8859-1'
        #print bb
        return bb

    return data

#------------------------------------------
# dispaly main menue
#------------------------------------------
@login_required
def index(request):

    try:    
        Settings.objects.get(pk=1)
    except: # das Programm wird das erste mal ausgefuehrt
        erststart = True
        aa = []
        alle_hallen = ''
        akt_uebers  = ''
        id_aktiv    = '0'
        t = DEFAULT_STR_KEIN_TURNIER_AKTIV
        n = Settings.objects.create(anzeige='1',aktives_turnier=t,aktives_turnier_id='0', online_turnier_id='0')
        online_turnier_id = '0'
        n.save()
    else:
        erststart    = False
        q_settings   = Settings.objects.get(pk=1)    # DB einträge für Settings Tabelle holen
        aa           = q_settings.aktives_turnier    # Eintrag aktives_turnier holen
        id_aktiv     = q_settings.aktives_turnier_id # Eintrag aktives_turnier_id holen, wenn 0 keines aktiv
        online_turnier_id = q_settings.online_turnier_id

        if (id_aktiv == '0'):
            # kein Turnier aktiv
            akt_uebers = ''
        else:   
            q_akt_turniere = Turnier.objects.get(pk=q_settings.aktives_turnier_id)
            akt_uebers     = q_akt_turniere.ueberschrift
        
        alle_hallen  = Spielort.objects.all()

        # Sind die Berechtigungsgruppen schon angelegt
        try:
            group = Group.objects.get(name='Turnierleitung')
        except: #nein
            group        = Group.objects.get_or_create(name='Turnierleitung')
            group        = Group.objects.get(name='Turnierleitung')
            content_type = ContentType.objects.get(app_label='turnier1', model='turnier')
            
            per = Permission.objects.create(codename = 'turnier_verwalten',
                                                name = 'Kann Turniere verwalten',
                                        content_type = content_type)
            group.permissions.add(per)

            content_type = ContentType.objects.get(app_label='turnier1', model='spiel')

            per_sp1 = Permission.objects.create(codename = 'spiele_admin',
                                                    name = 'Kann Spiele eines Turniers administrieren',
                                            content_type = content_type)
            group.permissions.add(per_sp1)

            per_sp2 = Permission.objects.create(codename = 'spiele_eingeben',
                                                    name = 'Kann Ergebnise zu einem Spiel eingeben',
                                            content_type = content_type)
            group.permissions.add(per_sp2)

        try:
            group = Group.objects.get(name='Ergebniseingabe')
        except: #nein
            group        = Group.objects.get_or_create(name='Ergebniseingabe')
            group        = Group.objects.get(name='Ergebniseingabe')
            
            group.permissions.add(per_sp2)

    context = RequestContext(request,{
        'user'             : request.user,
        'erststart'        : erststart,
        'alle_hallen'      : alle_hallen,
        'akt_turnier'      : aa,
        'akt_ueberschrift' : akt_uebers,
        'id_aktiv'         : id_aktiv,
        'online_turnier_id': online_turnier_id,
    })
    template = loader.get_template('turnier1/index.html')    
    return HttpResponse(template.render(context))
   
#----------------------------------------------------
# tournament management - display all tournaments
#----------------------------------------------------
@login_required
@permission_required('turnier1.turnier_verwalten',login_url='/nopermission/')
def turniere(request):

    if request.method == 'POST':

        # Sollen Turnier gelschöscht werden? Auslesen aller Checkboxen, dann löschen
        alle_turniere = Turnier.objects.order_by('-pub_date')
        t_ids = []
        for turnier in alle_turniere:
            try:
                d = request.POST[str(turnier.id)] # choice aus dem Form holen
            except (KeyError):
                pass
            else:
                t_ids.append(d)

        all_settings    = Settings.objects.get(pk=1)
        aktiv_tunier_id = all_settings.aktives_turnier_id

        for i in range(0, len(t_ids)):
            if (t_ids[i] == aktiv_tunier_id): # aktives Turnier kann nicht gelöscht werden
                pass
            else:
                Turnier.objects.filter(id=int(t_ids[i])).delete()

            # Wenn kein Trurnier mehr vorhanden ist muss auch das aktiverte Turnier gelöscht werden
            n = Turnier.objects.all()[:1]
            if len(n) == 0 :
                q_settings = Settings.objects.get(id=1)
                q_settings.aktives_turnier='kein Turnier aktiv'
                q_settings.aktives_turnier_id = '0'
                q_settings.save()
      
    # Liste der Turnier ausgeben  
    alle_turniere   = Turnier.objects.order_by('-pub_date')
    q_settings      = Settings.objects.get(pk=1)
    aktiv_tunier    = q_settings.aktives_turnier
    aktiv_tunier_id = q_settings.aktives_turnier_id
    q_spielorte     = Spielort.objects.all()

    # Ist die Liste der Truniere leer?
    if not alle_turniere: # Liste leer

        max_spielorte = ''
        turr = []
    else:    

        # Ermittlung der max Anzahl an Spielorten die für ein Turnier vorhanden sind - ergeniss ist max(m)
        m = []
        for ort in q_spielorte: #lauf durch alle Spielorte die da sind
            tur_id = ort.turnier
            m.append(Spielort.objects.filter(turnier=tur_id).count())

        # leere Array erzeugen vom type: turnier.id, halle, turnier.id, halle
        turr = []
        for n in range(0,max(m)*alle_turniere.count()):
            turr.append(['',''])

        #Spielorte in das Array legen
        q_alle_turniere = Turnier.objects.all()
        q_alle_spielorte = Spielort.objects.all()

        n=0
        for turnier1 in q_alle_turniere:
            
            q_aa = Spielort.objects.filter(turnier=turnier1.id) # alle Spielorte für das Turnier

            i=n*max(m)
            for j in range(0,max(m)):
                turr[i][0]= turnier1.id
                i +=1

            i=n*max(m)    
            for orte in q_aa:
                print orte.hallen_name
                #turr[i][1]= str(orte.hallen_name)
                turr[i][1]= orte.hallen_name
                i +=1
            n +=1
        
        max_spielorte = ''
        for i in range(0,max(m)):
            max_spielorte = max_spielorte +'x' # Erzeugt xxx für drei Spielorte

    context ={
        'alle_turniere': alle_turniere,
        'aktiv_tunier' : aktiv_tunier,
        'aktiv_tunier_id' : int(aktiv_tunier_id),
        'q_spielorte'     : q_spielorte,
        'max_spielorte' : max_spielorte,
        'turr' : turr,
    }
    return render(request,'turnier1/turnier.html',context)
#----------------------------------------------------
# edit the selected tournament
#----------------------------------------------------    
@login_required
@permission_required('turnier1.turnier_verwalten',login_url='/nopermission/')
def turnier_edit(request,turnier_id):
    
    hallenFormSet = inlineformset_factory(Turnier, Spielort, form=SpielorteForm, extra=7, can_delete=False)
    akt_turnier   = get_object_or_404(Turnier, pk=turnier_id)
    form_halle    = hallenFormSet(instance=akt_turnier)
    form_turnier  = TurnierAnlegenForm(instance=akt_turnier)
    
    if request.method == 'POST':
        
        form_turnier = TurnierAnlegenForm(request.POST,instance=akt_turnier) # Daten des Forms (forms.py) einlesen

        if form_turnier.is_valid(): # sind alle Felde richtig eingegeben

            # Daten aus dem Form auslesen und auf DB Schreiben
            new_store  = form_turnier.save()

            # falls sich das aktive Turnier geändert hat muss auch das aktualisiert werden
            q_settings = Settings.objects.get(pk=1)
            q_turnier  = Turnier.objects.get(pk=turnier_id)

            # der name des aktiven turniers muss aktualsiert werden
            if (q_settings.aktives_turnier_id == turnier_id): 
                q_settings.aktives_turnier = q_turnier.turnier_name
                q_settings.save()

            form_halle = hallenFormSet(request.POST, request.FILES, instance=new_store)


            if form_halle.is_valid():

                form_halle.save() # wenn leer wurde keine Halle angelegt
                q_ab = Spielort.objects.filter(turnier=new_store) #gibt es schon eine Halle für das Turnier?
                
                # alle löschen die leer sind
                for halle in q_ab:
                    if halle.hallen_name == 'Halle': # ist die Halle leer dann löschen
                        Spielort.objects.filter(pk=halle.id).delete()

                q_ab = Spielort.objects.filter(turnier=new_store) # alle Hallen holen

                if  not q_ab: # ist erster leer dann setzten
                    new_store.spielort_set.create(hallen_name='Halle 1', farbe='#ffffff')

                return HttpResponseRedirect('/turnier/edit/') # Ruecksprung

    context ={
        'akt_turnier': akt_turnier,
        'turnier_id'   : turnier_id,
        'form_halle'  : form_halle,
        'form_turnier' : form_turnier,
    }
    return render(request,'turnier1/turnier_edit.html',context)

#----------------------------------------------------
# create a new tournament 
#----------------------------------------------------
@login_required
@permission_required('turnier1.turnier_verwalten',login_url='/nopermission/')
def turnier_create(request):

    # wurde bisher noch kein Turnier angelegt?
    aa = Turnier.objects.all()
    if aa:
        erstes_turnier = False
    else:
        erstes_turnier = True
    
    hallenFormSet = inlineformset_factory(Turnier, Spielort, form=SpielorteForm, extra=7, can_delete=False)
    #akt_turnier   = get_object_or_404(Turnier, pk=turnier_id)
    form_halle    = hallenFormSet()
    form_turnier  = TurnierAnlegenForm()

    if request.method == 'POST':
        form_turnier = TurnierAnlegenForm(request.POST) # Daten des Forms (forms.py) einlesen
        
        if form_turnier.is_valid(): # sind alle Felde richtig eingegeben

            new_store  = form_turnier.save() # inhalt des forms speichern
            form_halle = hallenFormSet(request.POST, request.FILES, instance=new_store)

            if form_halle.is_valid():

                form_halle.save()
                q_ab = Spielort.objects.filter(turnier=new_store) #gibt es schon eine Halle für das Turnier?
                
                # alle löschen die leer sind
                for halle in q_ab:

                    if halle.hallen_name == "Halle": # ist die Halle leer dann löschen
                        Spielort.objects.filter(pk=halle.id).delete()

                q_ab = Spielort.objects.filter(turnier=new_store) # alle Hallen holen

                if  not q_ab: # ist erster leer dann setzten es muss min. eine Halle angelegt sein
                    new_store.spielort_set.create(hallen_name='Halle 1', farbe= '#ffffff')

                if erstes_turnier: # es wurde das aller erste Turnier angelegt
                    
                    # kein Turnier ist aktiv
                    q_n                    = Settings.objects.get(pk=1)
                    q_n.aktives_turnier    = DEFAULT_STR_KEIN_TURNIER_AKTIV
                    q_n.aktives_turnier_id = '0'
                    q_n.save()
                    #return HttpResponseRedirect('/turnier/') # Ruecksprung

                return HttpResponseRedirect('/turnier/edit/') # Ruecksprung
   
    context = {
        'erstes_turnier': erstes_turnier,
        'form_halle'    : form_halle,
        'form_turnier'  : form_turnier,
    }
    return render(request,'turnier1/turnier_create.html',context)

#----------------------------------------------------
# activate a tournament
#----------------------------------------------------
@login_required
@permission_required('turnier1.turnier_verwalten',login_url='/nopermission/')
def aktiviate_turnier(request):
  
    alle_turniere = Turnier.objects.order_by('pub_date')
    akt_turnier   = Settings.objects.get(pk=1)

    if request.method == 'POST':

        #alle_turniere = Turnier.objects.all()
        try:
            t_id=request.POST['choice'] # choice aus dem Form holen
        except (KeyError):
            pass
        else:
            flag_set_online = request.POST.get('check','off') # wert ist 'on' wenn gesetzt

            try:
                q_turnier = get_object_or_404(Turnier, pk=t_id)     
            except:
                ueberschrift          = ''
                turnier_name          = DEFAULT_STR_KEIN_TURNIER_AKTIV
                new_online_turnier_id = '0'
            else: 
                ueberschrift          = q_turnier.ueberschrift         
                turnier_name          = q_turnier.turnier_name

                # es kann nur ein turnier online gehen welches auch aktiv ist
                if flag_set_online == 'on' and t_id == akt_turnier.aktives_turnier_id:
                    new_online_turnier_id = t_id
                else:
                    new_online_turnier_id = '0'

            context = {
                'akt_turnier'          : akt_turnier.aktives_turnier,
                'ueberschrift'         : ueberschrift,
                'turnier_name'         : turnier_name,
                'turnier_id'           : t_id,
                'set_online_old'       : akt_turnier.online_turnier_id,
                'new_online_turnier_id': new_online_turnier_id,
            }
            return render(request,'turnier1/turnier_aktivate_confirm.html',context)

    # Lister der angelegten Turnier ausgeben
    akt_turnier   = Settings.objects.get(pk=1)

    if akt_turnier.aktives_turnier_id != '0': # ist ein Turnier aktiv
        q_turnier        = Turnier.objects.get(pk=int(akt_turnier.aktives_turnier_id))
        akt_ueberschrift = q_turnier.ueberschrift
    else:
        akt_ueberschrift = ''

    context ={
        'alle_turniere'     : alle_turniere,
        'akt_turnier'       : akt_turnier.aktives_turnier,
        'akt_ueberschrift'  : akt_ueberschrift,
        'akt_turnier_id'    : int(akt_turnier.aktives_turnier_id),
        'online_turnier_id' : akt_turnier.online_turnier_id,
    }
    return render(request,'turnier1/turnier_aktivate.html',context)
#------------------------------------------------------
#   Confirm activate tournament
#------------------------------------------------------
@login_required
@permission_required('turnier1.turnier_verwalten',login_url='/nopermission/')
def aktiviate_turnier_confirm(request, turnier_id):

    online_turnier_id = request.GET.get('id','') # online_turnier_id wurde in der URL als Paramter übergeben

    q_settings = get_object_or_404(Settings, pk=1)
    
    if (turnier_id == '0'): # kein Turnier soll aktiv sein
        
        q_settings.aktives_turnier    = DEFAULT_STR_KEIN_TURNIER_AKTIV
        q_settings.aktives_turnier_id = '0'
        q_settings.online_turnier_id  = '0'
        q_settings.save()

    else: # eine Turnier soll aktiviert werden -> confirm

        q_turnier = get_object_or_404(Turnier, pk=turnier_id)

        #speicher in DB Settings
        q_settings.aktives_turnier    = q_turnier.turnier_name
        q_settings.aktives_turnier_id = turnier_id
        q_settings.online_turnier_id  = online_turnier_id
        q_settings.save()

    return HttpResponseRedirect('/turnier/aktivate') # Ruecksprung
    
#----------------------------------------------------
# upload a tournament plan
#----------------------------------------------------
@login_required
@permission_required('turnier1.turnier_verwalten',login_url='/nopermission/')
def turnier_load(request):
    if request.method == 'POST':

        #alle_turniere = Turnier.objects.all()
        try:
            t_id=request.POST['choice'] # choice aus dem Form holen
        except (KeyError):
            pass
        else:
            if (t_id == '0'): # es wurde keine Turnier ausgewählt
                pass
            else:
                path = '/turnier/edit/load/' + t_id

                return HttpResponseRedirect(path) # Sprung zu Fileeingabe

    alle_turniere = Turnier.objects.order_by('pub_date')
    q_settings    = Settings.objects.get(pk=1)

    # Lister der angelegten Turnier ausgeben
    context = {
        'alle_turniere' : alle_turniere,
        'akt_turnier'   : q_settings.aktives_turnier,
        'akt_turnier_id': int(q_settings.aktives_turnier_id),
    }
    return render(request,'turnier1/turnier_load.html',context)

#--------------------
@login_required
@permission_required('turnier1.turnier_verwalten',login_url='/nopermission/')
def turnier_load_file(request, turnier_id):

    if request.method == 'POST':

        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():

            data_f = request.FILES['file'].read() # File auslesen

            fd=try_utf8(data_f) # nach UTF-8 codieren

            # ist es CSV File?
            try:
                portfolio = [row for row in csv.reader(fd.splitlines(),delimiter=';')]
            except:
                #kein CSV-File
                file_name = request.FILES['file']

                context = {
                    'file_name' : file_name,
                }
                return render(request,'turnier1/turnier_load_file_fail.html',context)

            else:
                plan = []

                for row in portfolio:
                    plan.append(row)
                fd = request.FILES['file'].close()
                
                tt = Turnier.objects.get(pk=turnier_id) # Spiel abhängig von Turnier
                
                # alle Spielorte für das Turnier löschen
                Spielort.objects.filter(turnier=turnier_id).delete()

                # alle Spiele für das Turnier löschen
                Spiel.objects.filter(turnier=turnier_id).delete()

                # CSV File aufbereiten
                for i in range(0, len(plan)): # Daten aus dem File in den Datensatzt speicher
                    
                    if len(plan[i][0]) < 4 :  # wenn kein vernümpftige Zeit mehr kommt abbrechen
                        break
                    
                    # für alle drei Hallen - in 6er Schritten
                    for n in range(0,18,6): # damit n=0 n=6 n=12

                        if len(plan[i][n]) < 4 :  # wenn kein vernümpftige Zeit mehr kommt abbrechen
                            break
                        
                        # Nachsehen ob es ein Gruppenspiel ist
                        aa = plan[i][2+n][2:3] # aus spiel_name den spiel_typ herausholen
                        if (aa == '1'):  
                            sp_type = 'Gruppe 1'
                        elif (aa == '2'):
                            sp_type = 'Gruppe 2'
                        elif (aa == '3'):
                            sp_type = 'Gruppe 3'
                        elif (aa == '4'):
                            sp_type = 'Gruppe 4'
                        else:
                            sp_type = ''

                        # die Hallen speichern, alle Hallen aus der ersten Zeile holen
                        if i == 0:
                            tt.spielort_set.create(hallen_name=plan[i][1+n])

                        tt.spiel_set.create(zeit=plan[i][n], halle=plan[i][1+n],  spiel_name=plan[i][2+n],
                                            jugend=plan[i][2+n][0:1], heim=plan[i][3+n], gast=plan[i][4+n],
                                            schiri=plan[i][5+n],    spiel_type=sp_type)

                # CSV load success
                q_turnier    = get_object_or_404(Turnier, pk=turnier_id)
                name_turnier = q_turnier.turnier_name

                context = {
                    'name_turnier' : name_turnier,
                }
                return render(request,'turnier1/turnier_load_file_success.html',context)

        else:
            form         = UploadFileForm
            q_turnier    = get_object_or_404(Turnier, pk=turnier_id)
            name_turnier = q_turnier.turnier_name

            # Lister der angelegten Turnier ausgeben
            context = {
                'name_turnier' : name_turnier,
                'turnier_id'   : turnier_id,
                'form'         : form,
            }
            return render(request,'turnier1/turnier_load_file.html',context)

        return HttpResponseRedirect('/turnier/edit/load')

    form         = UploadFileForm
    q_turnier    = get_object_or_404(Turnier, pk=turnier_id)
    name_turnier = q_turnier.turnier_name

    # Lister der angelegten Turnier ausgeben
    context = {
        'name_turnier' : name_turnier,
        'turnier_id'   : turnier_id,
        'form'         : form,
    }
    return render(request,'turnier1/turnier_load_file.html',context)















