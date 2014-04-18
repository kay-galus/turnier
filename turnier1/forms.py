# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, Textarea
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from turnier1.models import Spiel, Turnier, Spielort, Settings


JUGEND_CHOICES = (
    ('m', 'm'),
    ('w','w'),
    ('Minis','Minis'),
    ('EJ','E-Jugend'),
    ('sonst','sonst'),

)
GRUPPE_TYPE_CHOICES = (
        ('Gruppe 1', 'Gruppe 1'),
        ('Gruppe 2', 'Gruppe 2'),
        ('Gruppe 3', 'Gruppe 3'),
        ('Gruppe 4', 'Gruppe 4'),
        ('Halbfi.', 'Halbfi.'),
        ('Finale', 'Finale'),
        ('Platz', 'Platz'),
        ('sonst','sonst'),
)

COLORS = (
    ('#ffffff','weiss'),
    ('#a3e8ff','hell-blau'),
    ('#e0d5ff', 'hell-lila'),
    ('#ffe1e0', 'hell-rot'),
    ('#fff0dc', 'hell-gelb'),
    ('#e4f0dc','hell-gruen'),
    ('#efefef', 'hell-grau'),
)

ERROR_INVALID      = ' Zahl eingeben oder leer lassen!'
ERROR_MAX_VALUE    = ' Zahl kleiner 100 oder leer!'
ERROR_REQUIRED     = ' Feld darf nicht leer sein!'
ERROR_INVALID_TIME = ' Richtiges Zeitformat eingeben!'

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )

#-------------
class AdminListForm(forms.ModelForm):
    '''AdminListForm  Used to size the text input boxes'''

    class Meta:
        widgets = {   'zeit': forms.TimeInput(attrs={'size': 7,'format':'%H:%M'})
                   # , 'halle': forms.SelectMultiple(attrs={'size': 0})
                   # , 'jugend': forms.RadioSelect(attrs={'size': 5})
                    ,  'spiel_name': forms.TextInput(attrs={'size': 10}) 
                    , 'heim': forms.TextInput(attrs={'size': 25})
                    , 'toreH': forms.TextInput(attrs={'size': 2})
                    , 'toreG': forms.TextInput(attrs={'size': 2}) 
                    , 'gast': forms.TextInput(attrs={'size': 25})
                    , 'schiri': forms.TextInput(attrs={'size': 20})
                    , 'kampfgericht': forms.TextInput(attrs={'size': 20})
                 } 

#-----------
class TurnierAnlegenForm(ModelForm):
    class Meta:
        model = Turnier
        #exclude = ('pub_date',)
        fields = ['turnier_name', 'ueberschrift']

        help_texts = {
            'turnier_name': _('(z.B. A-Jugend 2014)'),
            'ueberschrift': _('(z.B. LEW Jugend CUP 2014)'),
        }
        error_messages = {
            'turnier_name': {'required': _(ERROR_REQUIRED), },
            'ueberschrift': {'required': _(ERROR_REQUIRED), },
        }    

#-----------
class SpielorteForm(ModelForm):

    farbe = forms.ChoiceField(choices=COLORS, initial=1)

    class Meta:
        model = Spielort
        fields = ['hallen_name', 'farbe']
        
        error_messages = {
            'hallen_name': {'required': _(ERROR_REQUIRED), },
        } 

#---------
class UploadFileForm(forms.Form):
    file  = forms.FileField()

#---------
class SettingsForm(ModelForm):
    class Meta:
        model = Settings
        exclude = ('anzeige',)

#--------
class EingabeHallenForm(ModelForm):

    class Meta:
        model = Spiel
        fields = ['toreH', 'toreG']

        error_messages = {
            'toreH': {'invalid': _(ERROR_INVALID),
                       'max_value': _(ERROR_MAX_VALUE), },
            'toreG': {'invalid': _(ERROR_INVALID),
                      'max_value': _(ERROR_MAX_VALUE), },
          } 

#--------
class EditSpielForm(forms.ModelForm):

    # auslesen der hallen das db und setzten des choicefields immer wenn form benutzt wird
    def __init__(self, *args, **kwargs):
        
        super(EditSpielForm, self).__init__(*args, **kwargs)

        q_settings   = Settings.objects.get(pk=1)     # Querry auf settings
        akt_id       = q_settings.aktives_turnier_id  # ID aktives Turnier
        
        if akt_id != '0':
            sp = Spielort.objects.filter(turnier=akt_id)
    
            aa = [(halle.hallen_name,halle.hallen_name) for halle in sp]

            self.fields['halle'] = forms.ChoiceField(choices=aa, initial=1)

    zeit = forms.TimeField(
                            required=False,
                            error_messages={'invalid':ERROR_INVALID_TIME},
                            widget=forms.TimeInput(format='%H:%M',attrs={'size': 6}))

    jugend     = forms.ChoiceField(choices=JUGEND_CHOICES, initial=0)
    spiel_type = forms.ChoiceField(choices=GRUPPE_TYPE_CHOICES, initial=0)
 
    class Meta:
        model = Spiel
        
        fields = ['zeit','spiel_name', 'halle', 'jugend','spiel_type', 'heim', 'toreH',
                  'toreG', 'gast', 'schiri', 'kampfgericht']

        widgets = {'spiel_name': forms.TextInput(attrs={'size': 10}),
                   'halle': forms.TextInput(attrs={'size': 12}),
                  }
        error_messages = {
                    'hallen_name': {'required': _(ERROR_REQUIRED), },
                    'toreH': {'invalid': _(ERROR_INVALID),
                               'max_value': _(ERROR_MAX_VALUE), },
                    'toreG': {'invalid': _(ERROR_INVALID),
                              'max_value': _(ERROR_MAX_VALUE), },
                  } 

#----------------
class EditSpiel11Form(forms.ModelForm):

    # auslesen der hallen das db und setzten des choicefields immer wenn form benutzt wird
    def __init__(self, *args, **kwargs):
        super(EditSpiel11Form, self).__init__(*args, **kwargs)

        q_settings   = Settings.objects.get(pk=1)     # Querry auf settings
        akt_id       = q_settings.aktives_turnier_id  # ID aktives Turnier
        
        if akt_id != '0':
            sp = Spielort.objects.filter(turnier=akt_id)
    
            aa = [(halle.hallen_name,halle.hallen_name) for halle in sp]

            self.fields['halle'] = forms.ChoiceField(choices=aa, initial=1)
            #self.fields['halle'] = forms.ModelChoiceField(queryset=sp, initial=1)
            #self.fields['halle'] = forms.ModelChoiceField(choices=tuple(aa), initial=1)
           
    zeit = forms.TimeField(
                            required=False,
                            error_messages={'invalid':ERROR_INVALID_TIME},
                            widget=forms.TimeInput(format='%H:%M',attrs={'size': 6}))


    jugend     = forms.ChoiceField(choices=JUGEND_CHOICES, initial=0)
    spiel_type = forms.ChoiceField(choices=GRUPPE_TYPE_CHOICES, initial=1)

    class Meta:
        model = Spiel
        
        fields = ['zeit','spiel_name', 'halle', 'jugend','spiel_type', 'heim',
                 'gast', 'schiri', 'kampfgericht']

        widgets = {'spiel_name': forms.TextInput(attrs={'size': 10}),
                   #'halle': forms.TextInput(attrs={'size': 12}),
                  }
        error_messages = {
                    #'hallen_name': {'required': _(ERROR_REQUIRED), },
                    'toreH': {'invalid': _(ERROR_INVALID),
                               'max_value': _(ERROR_MAX_VALUE), },
                    'toreG': {'invalid': _(ERROR_INVALID),
                              'max_value': _(ERROR_MAX_VALUE), },
                  } 

#-------------------
class TurnierAnlegen11Form(ModelForm):
    class Meta:
        model  = Turnier
        fields = ['turnier_name', 'ueberschrift']

        widgets = {'turnier_name': forms.TextInput(attrs={'readonly':'readonly'}),
                   'ueberschrift': forms.TextInput(attrs={'readonly':'readonly'}),
                   }









