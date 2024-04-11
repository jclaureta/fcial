import datetime
from time import time

from django.db import models




types = [('Student','Student'),('Professor','Professor')]
class Profile(models.Model):
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=70)
    date = models.DateField()
    phone = models.BigIntegerField()
    email = models.EmailField()
    term = models.IntegerField()
    program = models.CharField(max_length=200)
    status = models.CharField(choices=types,max_length=20,null=True,blank=False,default='employee')
    present = models.BooleanField(default=False)
    image = models.ImageField()
    updated = models.DateTimeField(auto_now=True)
    section = models.CharField(max_length=200)
    studentid = models.CharField(max_length=200)
    def __str__(self):
        return self.first_name +' '+self.last_name
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)


class LastFace(models.Model):
    last_face = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.last_face

