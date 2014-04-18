# -*- coding: utf-8 -*-

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

#-----------------------------------
class Turnier(models.Model):
      
    turnier_name   = models.CharField('Name des Turniers',max_length=20, default='Turniername')
    pub_date       = models.DateTimeField(auto_now=True)
    ueberschrift   = models.CharField('Turnier-Überschrift',max_length=70,default='Überschrift',blank=True)

    def __unicode__(self):
        return u'%s' % (self.turnier_name)
        
    class Meta:
        verbose_name_plural = "Turniere"

        #permissions = (
        #    ("turnier_verwalten", "Kann Turniere verwalten"),

        #)

#-------------------------------------- 
class Spiel(models.Model):
 
    turnier    = models.ForeignKey(Turnier) #turnier_id
    zeit       = models.TimeField(max_length=5, blank=True, null=True)
    spiel_name = models.CharField(max_length=12, blank=True, verbose_name='Spiel') # z.B. wC1
    halle      = models.CharField(max_length=25, blank=True, default='Halle 1')
    jugend     = models.CharField(max_length=6, blank=True, default='m')
    spiel_type = models.CharField(max_length=8, blank=True, default='Platz')
    heim       = models.CharField(max_length=25, blank=True,)     
    MAX_SMALL_INT = 99
    toreH      = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='H', max_length=2,
                                                    validators=[MinValueValidator(0),MaxValueValidator(99)])
    toreG      = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='G', 
                                                    validators=[MinValueValidator(0),MaxValueValidator(99)])
    gast       = models.CharField(max_length=25, blank=True,)
    schiri     = models.CharField(max_length=30, blank=True,verbose_name='Schiedsrichter')
    kampfgericht  = models.CharField(max_length=30, blank=True)

    def __unicode__(self):
        return u'%s %s %s %s %s %s %s %s %s %s' % (self.halle, self.spiel_name, self.schiri,
                                                   self.kampfgericht, self.spiel_type,
                                                   self.heim, self.gast, self.toreH, self.toreG, self.jugend)
        
    class Meta:
        verbose_name_plural = "Spiele"

        #permissions = (
        #    ("spiele_admin",    "Kann Spiele eines Turniers administrieren"),
        #    ("spiele_eingeben", "Kann Ergebnise zu einem Spiel eingeben"),
        #)   

#---------------------------------
class Settings(models.Model):
    
    anzeige            = models.CharField(max_length=1, default='1', blank=False) # Anzeige auf Spielmonitor
    aktives_turnier    = models.CharField(max_length=20,default='kein Turnier aktiv',blank=True)
    aktives_turnier_id = models.CharField(max_length=3, default='0') # 0=kein gültiger Eintrag
    online_turnier_id  = models.CharField(max_length=1, default='0') # 0=Spielplan des Turniers nicht online

    def __unicode__(self):
        return u'%s %s %s %s' % (self.anzeige, self.aktives_turnier, self.aktives_turnier_id, self.online_turnier_id)

    class Meta:
        verbose_name_plural = "Settings"

#-----------------------------------
class Spielort(models.Model):

    turnier     = models.ForeignKey(Turnier) #turnier_id
    hallen_name = models.CharField(max_length=15, default='Halle', blank=True)
    farbe       = models.CharField(max_length=8, default= 'weiss', blank=True)

    #def __unicode__(self):
        #return u'%s s%' % (self.hallen_name, self.farbe)
        
    class Meta:
        verbose_name_plural = "Spielorte"

      


    
    