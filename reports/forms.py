from django import forms
from django.forms.models import ModelChoiceField
from .models import Client, Tester, Lab, Report 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model







class ReportKeywordFilterForm(forms.Form):
    keywords = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
            super(ReportKeywordFilterForm, self).__init__(*args, **kwargs)
            self.fields['keywords'].widget.attrs.update({
                'class': 'form-control form-control-navbar', 
                'placeholder':'Search Reports', 
                'type': 'search',
                'aria-label': 'search',
                })



class ClientBasicFilterForm(forms.Form):
    full_name = forms.CharField(max_length=512, required=False)
    def __init__(self, *args, **kwargs):
            super(ClientBasicFilterForm, self).__init__(*args, **kwargs)
            self.fields['full_name'].widget.attrs.update({'class': 'form-control', 'placeholder':'Name'})





class ReportForm(forms.ModelForm):
    class Meta:
        model =  Report
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super( ReportForm, self).__init__(*args, **kwargs)
        field_keys = self.fields.keys()
        for key in field_keys:
            self.fields[key].widget.attrs.update({'class': 'form-control'})
        self.fields['print_date'].widget.attrs.update({ 'class': 'form-control datetimepicker-input', 'data-target': '#report_print_date'})
        self.fields['collect_date'].widget.attrs.update({ 'class': 'form-control datetimepicker-input', 'data-target': '#report_collect_date'})
        self.fields['unit_date'].widget.attrs.update({ 'class': 'form-control datetimepicker-input', 'data-target': '#report_unit_date'})
        self.fields['details'].widget.attrs.update({ 'id': 'summernote'})

class ReportExClientForm(ReportForm):
    class Meta:
        model =  Report
        exclude = ('client',)

class ReportBasicFilterForm(forms.ModelForm):
    client =  ModelChoiceField(queryset=Client.objects.filter().order_by('-pk'), empty_label="All Clients", required=False)
    test_request = forms.CharField(max_length=512, required=False)
    print_date = forms.CharField(max_length=255, required=False)
    keyword = forms.CharField(max_length=512, required=False)

    class Meta:
            fields = [
                'test_request',
                'client',
                'print_date'
            ]
            model = Report

    def __init__(self, *args, **kwargs):
            super(ReportBasicFilterForm, self).__init__(*args, **kwargs)
            self.fields['test_request'].widget.attrs.update({'class': 'form-control', 'placeholder':'Type of Report'})
            self.fields['client'].widget.attrs.update({'class': 'form-control'})
            self.fields['print_date'].widget.attrs.update({ 'class': 'form-control datetimepicker-input', 'data-target': '#reportdatetime', 'placeholder':'Date'})


    # def __init__(self, *args, **kwargs):
    #     super( ReportExClientForm, self).__init__(*args, **kwargs)
    #     self.fields['type'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['result'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['desired_result'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['details'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['desired_result'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['performed_by'].widget.attrs.update({'class': 'form-control'})  
    #     self.fields['lab'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['date'].widget.attrs.update({ 'class': 'form-control datetimepicker-input', 'data-target': '#reportdatetime'})        

class ReportAdvanceFilterForm(forms.ModelForm):
    client =  ModelChoiceField(queryset=Client.objects.filter().order_by('-pk'), empty_label="All Clients", required=False)
    test_request = forms.CharField(max_length=512, required=False)
    result = forms.CharField(max_length=255, required=False)
    desired_result = forms.CharField(max_length=255, required=False)
    details = forms.CharField(max_length=512, required=False)
    performed_by =  ModelChoiceField(queryset=Tester.objects.filter().order_by('-pk'), empty_label="All Technicians", required=False)
    lab =  ModelChoiceField(queryset=Lab.objects.filter().order_by('-pk'), empty_label="All Labs", required=False)
    print_date = forms.CharField(max_length=255, required=False)
    keyword = forms.CharField(max_length=512, required=False)

    class Meta:
        model =  Report
        fields = ['client', 'test_request','result','desired_result','details','performed_by','lab', 'print_date']

    def __init__(self, *args, **kwargs):
        super(ReportAdvanceFilterForm, self).__init__(*args, **kwargs)
        self.fields['test_request'].widget.attrs.update({'class': 'form-control', 'placeholder':'Type of Report'})
        self.fields['print_date'].widget.attrs.update({ 'class': 'form-control datetimepicker-input', 'data-target': '#reportdatetime', 'placeholder':'Date'})
        self.fields['result'].widget.attrs.update({'class': 'form-control'})
        self.fields['details'].widget.attrs.update({'class': 'form-control'})
        self.fields['desired_result'].widget.attrs.update({'class': 'form-control'})
        self.fields['performed_by'].widget.attrs.update({'class': 'form-control'})  
        self.fields['lab'].widget.attrs.update({'class': 'form-control'})
        self.fields['client'].widget.attrs.update({'class': 'form-control'})



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
