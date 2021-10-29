from django.contrib import admin

from reports.models import Client, Lab, Report, Tester

# Register your models here.
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    pass

@admin.register(Tester)
class TesterAdmin(admin.ModelAdmin):
    pass

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    pass