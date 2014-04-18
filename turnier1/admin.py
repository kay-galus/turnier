# -*- coding: utf-8 -*-

from django.contrib import admin
from turnier1.models import Spiel, Turnier, Settings, Spielort
from django.forms import TextInput
from django.db import models
from forms import AdminListForm


#class SpielAdminInline(admin.TabularInline):
#    model = Spiel   # from models.py
#    form  = AdminListForm      # from forms.py, sets the size attributes for the input boxes
#    extra = 0


#class PlanAdmin(admin.ModelAdmin):

 #   fieldsets = [
  #      ('Aktuelles Turnier',{'fields': ['turnier_name']}),
 #       ('Date information',  {'fields': ['spielplan_file']}),
  #  ]

 #   inlines = [
  #      SpielAdminInline,
   # ]

    #def time_format(self,obj):
    #    return obj.zeit.strftime("%H:%M")

    #time_format.short_description = 'Spielzeit' 

    #inlines = [ SpielAdminInline,]
    #linline=('SpielAdminInline',)
    #formfield_overrides = {
     #   models.CharField: {'widget': TextInput(attrs={'size': '25'})},
    #}

    #list_display = ('time_format','halle','jugend','spiel_name','heim','toreH','toreG',
     #               'gast','schiri','kampfgericht')

    #list_editable = ('spiel_name','heim','gast','schiri','kampfgericht','toreG','toreH')
    #ordering = ('zeit', 'halle')

admin.site.register(Turnier)
admin.site.register(Settings)
admin.site.register(Spielort)
admin.site.register(Spiel)


