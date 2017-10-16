# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import models

# Create your models here.
class zones(models.Model):
    class Meta:
        db_table = 'zones'
    Name = models.CharField(max_length=255,db_column='Name',blank = False,unique=True)
    Type = models.CharField(max_length=255,db_column='Type',blank = False,default='Forward')
    Switch = models.CharField(max_length=255,db_column='Switch',blank = False)

    def __unicode__(self):
        dicArray = {"Name":self.Name,"Type":self.Type,"Switch":self.Switch}
        return json.dumps(dicArray)

class records(models.Model):
    class Meta:
        db_table = 'records'
    Key = models.CharField(max_length=255, db_column='Key', blank=False)
    TTL = models.IntegerField(blank=True,null=True,default=3600)
    Type = models.CharField(max_length=255, db_column='Type', blank=False, default='A')
    Value = models.CharField(max_length=255, db_column='Value', blank=False)
    ZoneName = models.ForeignKey(zones,db_column='ZoneName',on_delete=models.CASCADE,to_field='Name')
    unique_together = ("Key", "Type","Value","ZoneName")

    def __unicode__(self):
        dicArray = {"ZoneName":self.ZoneName.Name,"Key":self.Key,"Type":self.Type,"TTL":self.TTL,"Value":self.Value}
        return json.dumps(dicArray)

class logs(models.Model):
    class Meta:
        db_table = 'logs'
    ID = models.AutoField(max_length=20,db_column='ID',primary_key=True)
    Time = models.DateTimeField(auto_now=False,db_column='Time', auto_now_add=True,null=True)
    Object = models.CharField(max_length=255,db_column='Object',blank = True,null=True)
    Operation = models.CharField(max_length=255,db_column='Operation',blank = False)
    Detail = models.CharField(max_length=255,db_column='Detail',blank = True,null=True)

    def __unicode__(self):
        dicArray = {"Time":self.Time,"Object":self.Object,"Operation":self.Operation,"Detail":self.Detail}
        return json.dumps(dicArray)
