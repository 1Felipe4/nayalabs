from django import forms
from django.forms.models import ModelChoiceField
from .models import Client, Tester, Lab, Report 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

class ReportForm(forms.ModelForm):
    class Meta:
        model =  Report
        exclude = ('file',)

    def __init__(self, *args, **kwargs):
        super( ReportForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget.attrs.update({'class': 'form-control'})
        self.fields['result'].widget.attrs.update({'class': 'form-control'})
        self.fields['desired_result'].widget.attrs.update({'class': 'form-control'})
        self.fields['details'].widget.attrs.update({'class': 'form-control'})
        self.fields['client'].widget.attrs.update({'class': 'form-control'})
        self.fields['desired_result'].widget.attrs.update({'class': 'form-control'})
        self.fields['performed_by'].widget.attrs.update({'class': 'form-control'})  
        self.fields['lab'].widget.attrs.update({'class': 'form-control'})
        self.fields['date'].widget.attrs.update({ 'class': 'form-control datetimepicker-input', 'data-target': '#reportdatetime'})


class ClientForm(forms.ModelForm):
    class Meta:
        model =  Client
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super( ClientForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['sex'].widget.attrs.update({'class': 'form-control'})
        self.fields['id_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['dob'].widget.attrs.update({ 'class': 'form-control datetimepicker-input', 'data-target': '#clientdob'})


class TesterForm(forms.ModelForm):
    class Meta:
        model =  Tester
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super( TesterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})

class LabForm(forms.ModelForm):
    class Meta:
        model =  Lab
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super( LabForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})



class UserRegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = [ 'username', 'email', 'first_name', 'last_name',  'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Retype Password'})

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
