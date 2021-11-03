from django.db import models
from django.db.models.deletion import SET_NULL
from django.utils.translation import ugettext as _
import datetime
from django.utils import timezone
from django.urls import reverse

# Create your models here.
class Report(models.Model):
    test_request = models.CharField(max_length=512)
    result = models.CharField(max_length=255)
    desired_result = models.CharField(max_length=255)
    details = models.TextField()
    print_date = models.DateTimeField(default=timezone.now)
    client = models.ForeignKey("reports.Client", verbose_name=_("Client"), null=True, on_delete=models.SET_NULL)
    performed_by = models.ForeignKey("reports.Tester", verbose_name=_("Performed By"), null=True, blank=False , on_delete=SET_NULL)
    lab = models.ForeignKey("reports.Lab", verbose_name=_("Lab"), on_delete=models.CASCADE)
    collect_date = models.DateTimeField(default=timezone.now)
    order_type = models.CharField(max_length=255, default='EXTERNAL')
    insurance = models.CharField(max_length=255, default='PARTICULAR')
    company =  models.CharField(max_length=512, default='OCCUPATIONAL HEALTH SOLUTIONS')
    doc_id = models.CharField(max_length=255, null=True, blank=True)
    doctor = models.CharField(max_length=512, null=True, blank=True)
    unit_date = models.DateTimeField(default=timezone.now)
    department = models.CharField(max_length=255, default='IMMUNO')
    branch_no = models.CharField(max_length=3, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('report_detail', kwargs={'pk': self.pk})
          
    def __str__(self):
        name = self.test_request
        if(self.client):
            name = f'{self.client.full_name} {name}' 
        if(self.print_date):
            name = f'{name} - {self.print_date.date()}'   
        return name  
class Client(models.Model):
    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)
    sex = models.CharField(_('Sex'), max_length=100)
    id_number = models.CharField(_('ID Number'), max_length=255, null=True, blank=True)
    dob = models.DateField(_("Date of Birth"), auto_now=False, auto_now_add=False)

    @property
    def full_name(self):
        name = self.first_name + " " + self.last_name
        return name.strip()

    @property
    def age(self):
        today = datetime.date.today()
        years = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return f'{years} Years'

    def __str__(self):
        return self.full_name 

    def get_absolute_url(self):
        return reverse('client_detail', kwargs={'pk': self.pk})

class Tester(models.Model):
    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)
    signature = models.ImageField(_("Signature"), upload_to='signatures', height_field=None, width_field=None, max_length=None, null=True)
    @property
    def full_name(self):
        name = self.first_name + " " + self.last_name
        return name.strip()  

    @property
    def prepared_by(self):
        name = f'{self.first_name[0]}{self.last_name}'.upper()
        return name.strip()


    def __str__(self):
        return self.full_name 

    def get_absolute_url(self):
        return reverse('tester_detail', kwargs={'pk': self.pk})

class Lab(models.Model):
    name = models.CharField(_("Name"), max_length=512)
    header = models.ImageField(_("Header"), upload_to='headers', height_field=None, width_field=None, max_length=None, null=True)
    footer = models.ImageField(_("Footer"), upload_to='footers', height_field=None, width_field=None, max_length=None, null=True, blank=True)
    stamp = models.ImageField(_("Stamp"), upload_to='stamps', height_field=None, width_field=None, max_length=None, null=True)

    def __str__(self):
        return self.name 

    def get_absolute_url(self):
        return reverse('lab_detail', kwargs={'pk': self.pk})