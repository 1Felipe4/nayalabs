from django.db import models
from django.db.models.deletion import SET_NULL
from django.utils.translation import ugettext as _
import datetime
from django.utils import timezone
from django.urls import reverse

# Create your models here.
class Report(models.Model):
    type = models.CharField(max_length=512)
    result = models.CharField(max_length=255)
    desired_result = models.CharField(max_length=255)
    details = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    client = models.ForeignKey("reports.Client", verbose_name=_("Client"), on_delete=models.CASCADE)
    performed_by = models.ForeignKey("reports.Tester", verbose_name=_("Performed By"), null=True, blank=False , on_delete=SET_NULL)
    lab = models.ForeignKey("reports.Lab", verbose_name=_("Lab"), on_delete=models.CASCADE)
    file = models.FileField(_("File"), upload_to=None, max_length=100, null=True)

    
    def get_absolute_url(self):
        return reverse('report_detail', kwargs={'pk': self.pk})
          
    def __str__(self):
        name = self.type
        if(self.client):
            name = f'{self.client.full_name} {name}' 
        if(self.date):
            name = f'{name} - {self.date.date()}'   
        return name  
class Client(models.Model):
    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)
    sex = models.CharField(_('Sex'), max_length=100)
    id_number = models.CharField(_('ID Number'), max_length=255, unique=True)
    dob = models.DateField(_("Date of Birth"), auto_now=False, auto_now_add=False)

    @property
    def full_name(self):
        name = self.first_name + " " + self.last_name
        return name.strip()  

    def __str__(self):
        return self.full_name 

    def get_absolute_url(self):
        return reverse('client_detail', kwargs={'pk': self.pk})

class Tester(models.Model):
    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)

    @property
    def full_name(self):
        name = self.first_name + " " + self.last_name
        return name.strip()  

    def __str__(self):
        return self.full_name 

    def get_absolute_url(self):
        return reverse('tester_detail', kwargs={'pk': self.pk})

class Lab(models.Model):
    name = models.CharField(_("Name"), max_length=512)
    logo = models.ImageField(_("Logo"), upload_to=None, height_field=None, width_field=None, max_length=None)

    def __str__(self):
        return self.name 

    def get_absolute_url(self):
        return reverse('lab_detail', kwargs={'pk': self.pk})