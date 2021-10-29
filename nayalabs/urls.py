"""nayalabs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from reports.views import ( ClientCreateView, ClientDeleteView, ClientDetailView, ClientListView, ClientUpdateView, LabCreateView, LabDeleteView, LabDetailView, LabListView, LabUpdateView, ReportCreateView, ReportDeleteView, ReportDetailView, ReportListView, ReportUpdateView, TesterCreateView, TesterDeleteView, TesterDetailView, TesterListView, TesterUpdateView )
from reports import views as report_views
from django.contrib.auth import views as auth_views
from reports.forms import UserLoginForm
from django.conf.urls.static import static 
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('add-report', ReportCreateView.as_view(), name='report_new'),
    path('report/<int:pk>', ReportDetailView.as_view(), name='report_detail'),
    path('edit-report/<int:pk>', ReportUpdateView.as_view(), name='report_update'),
    path('delete-report/<int:pk>', ReportDeleteView.as_view(), name='report_delete'),
    path('reports', ReportListView.as_view(), name='report_list'),
    path('add-client', ClientCreateView.as_view(), name='client_new'),
    path('client/<int:pk>', ClientDetailView.as_view(), name='client_detail'),
    path('edit-client/<int:pk>', ClientUpdateView.as_view(), name='client_update'),
    path('delete-client/<int:pk>', ClientDeleteView.as_view(), name='client_delete'),
    path('clients', ClientListView.as_view(), name='client_list'),
    path('add-tester', TesterCreateView.as_view(), name='tester_new'),
    path('tester/<int:pk>', TesterDetailView.as_view(), name='tester_detail'),
    path('edit-tester/<int:pk>', TesterUpdateView.as_view(), name='tester_update'),
    path('delete-tester/<int:pk>', TesterDeleteView.as_view(), name='tester_delete'),
    path('testers', TesterListView.as_view(), name='tester_list'),
    path('add-lab', LabCreateView.as_view(), name='lab_new'),
    path('lab/<int:pk>', LabDetailView.as_view(), name='lab_detail'),
    path('edit-lab/<int:pk>', LabUpdateView.as_view(), name='lab_update'),
    path('delete-lab/<int:pk>', LabDeleteView.as_view(), name='lab_delete'),
    path('labs', LabListView.as_view(), name='lab_list'),
    path('dashboard', report_views.dashboard, name="dashboard"),
    path("", report_views.home),
    path('accounts/login/', auth_views.LoginView.as_view(template_name="accounts/login.html", authentication_form=UserLoginForm), name="login"),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name="accounts/login.html"), name='logout'),
    path("accounts/register/", report_views.register, name="register"),
    path("view-report/<int:pk>", report_views.some_view, name="report_view"),
    path('qr_code/', include('qr_code.urls', namespace="qr_code")),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

