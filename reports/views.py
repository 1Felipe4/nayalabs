from datetime import datetime
from functools import partial
from django.http.response import HttpResponse
from django.shortcuts import render
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm, mm
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.tables import Table, TableStyle
from reports.pdf import render_to_pdf
from reports.pdf_template import header_and_footer, myFirstPage, myLaterPages
#from reports.pdf_template import PAGESIZE, header_and_footer, myFirstPage, myLaterPages
from .forms import ClientBasicFilterForm, ClientForm, LabForm, ReportAdvanceFilterForm, ReportBasicFilterForm, ReportExClientForm, ReportForm, ReportKeywordFilterForm, TesterForm, UserRegisterForm
from .models import Client, Lab, Report, Tester
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView,
    UpdateView,
    DeleteView
    )
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, permission_required
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.conf import settings
from PIL import Image, ImageDraw
from reportlab.lib import colors, utils
import qrcode
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as pdfImage
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.admin.views.decorators import staff_member_required
import lxml.html.clean as clean
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
defaultPageSize = letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.contrib.staticfiles.storage import staticfiles_storage

def home(request):
    return redirect("dashboard")# or your url name
        

@login_required
@staff_member_required(login_url='/accounts/login/')
def dashboard(request):
    form = ReportBasicFilterForm()

    return render(request, 'report/dashboard.html', {'form':form})

@login_required
@staff_member_required(login_url='/accounts/login/')
def advanced_report_filtering(request):
    form = ReportAdvanceFilterForm()
    return render(request, 'report/advanced-search.html', {'form':form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form':form})

# Create your views here.
class ReportCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = "report/report-form.html"
    login_url = '/accounts/login/'
    
    def test_func(self):
        return self.request.user.is_staff

class ReportUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Report
    form_class = ReportForm    
    template_name = "report/report-form.html"

    def test_func(self):
        return self.request.user.is_staff

class ReportDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Report
    template_name = "report/report-detail.html"

    def test_func(self):
        return self.request.user.is_staff

class ReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Report
    template_name = "report/reports.html"
    ordering = ['-pk']

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        keywords_form = ReportKeywordFilterForm()
        context['keywords_form'] = keywords_form
        return context

    def test_func(self):
        return self.request.user.is_staff

@login_required    
@staff_member_required(login_url='/accounts/login/')
def filter_reports(request):
    object_list = Report.objects.all()
    if request.method == 'GET':
        form = ReportAdvanceFilterForm(request.GET)
        # keywords_form = ReportKeywordFilterForm(request.GET)
        if form.is_valid():
            test_request = form.cleaned_data.get('test_request')
            client = form.cleaned_data.get('client')
            result = form.cleaned_data.get('result')
            desired_result = form.cleaned_data.get('desired_result')
            performed_by = form.cleaned_data.get('performed_by')
            details = form.cleaned_data.get('details')
            lab = form.cleaned_data.get('lab')
            date_str = form.cleaned_data.get('print_date')
            if(client):
                object_list = object_list.filter(client__pk=client.pk)
            if(performed_by):
                object_list = object_list.filter(performed_by__pk=performed_by.pk)
            if(lab):
                object_list = object_list.filter(lab__pk=lab.pk)                
            if(test_request):
                object_list = object_list.filter(type__icontains=test_request)
            if(result):
                object_list = object_list.filter(result__icontains=result)
            if(desired_result):
                object_list = object_list.filter(desired_result__icontains=desired_result)
            if(details):
                object_list = object_list.filter(details__icontains=details)
            if(date_str):
                date = datetime.strptime(date_str, '%Y-%m-%d')
                object_list = object_list.filter(print_date__year = date.year)
                object_list = object_list.filter(print_date__month = date.month)
                object_list = object_list.filter(print_date__day = date.day)


    else:
        form = ReportBasicFilterForm()
    object_list = object_list.order_by('-pk')  

    return render(request, 'report/reports.html', {'form':form, 'object_list': object_list})

class ReportDeleteView(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, DeleteView):
    model = Report
    permission_required = 'report.delete_report' 
    template_name = "report/report-delete.html"
    success_url = '/reports'

    def test_func(self):
        return self.request.user.is_staff

class ClientCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "client/client-form.html"

    def test_func(self):
        return self.request.user.is_staff

@login_required
@staff_member_required(login_url='/accounts/login/')
def clientReportView(request, pk):
    client = get_object_or_404(Client, pk=pk)
    context = {}
    if request.method == 'POST':
        form = ReportForm(request.POST)
        context = {'form':form}
        if(form.is_valid()):
            report = form.save()
            return redirect('report_detail', report.pk)
    else:    
        form = ReportForm(initial={'client': client.pk})
        context = {'form': form}
    return render(request, 'report/report-form.html', context)

@login_required
@staff_member_required(login_url='/accounts/login/')
def add_report_with_client(request):
    if request.method == 'POST':
        form = ReportExClientForm(request.POST)
        client_form = ClientForm(request.POST)
        if form.is_valid():
            if(client_form.is_valid()):
                report = form.save(commit=False)
                client = client_form.save(commit=False)
                report.client = client
                client.save()
                report.save()
                client_form.save_m2m()
                form.save_m2m()
                return redirect('report_detail', report.pk)
    else:
        form = ReportExClientForm()
        client_form = ClientForm()
    
    return render(request, 'report/report-form.html', {'form':form, 'client_form':client_form})

class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Client
    form_class = ClientForm    
    template_name = "client/client-form.html"

    def test_func(self):
        return self.request.user.is_staff

class ClientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Client
    template_name = "client/client-detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        client = Client.objects.filter(pk=self.kwargs['pk']).first()
        recent_reports = Report.objects.filter(client__pk=client.pk).order_by('-pk')[:5]
        context['reports'] = recent_reports
        keywords_form = ReportKeywordFilterForm()
        context['keywords_form'] = keywords_form
        return context

    def test_func(self):
        return self.request.user.is_staff


class ClientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Client
    template_name = "client/clients.html"
    ordering = ['-pk']

    def test_func(self):
        return self.request.user.is_staff    

@login_required
@staff_member_required(login_url='/accounts/login/')
def filter_clients(request):
    object_list = Client.objects.all()
    if request.method == 'GET':
        form = ClientBasicFilterForm(request.GET)
        # keywords_form = ReportKeywordFilterForm(request.GET)
        if form.is_valid():
            full_name = form.cleaned_data.get('full_name')
            found = []
            if(full_name):
                if(object_list.filter(first_name__icontains = full_name)):
                    found = object_list.filter(first_name__icontains = full_name)
                    if(found.filter(last_name__icontains = full_name)):
                        found = object_list.filter(last_name__icontains = full_name)

                elif(object_list.filter(last_name__icontains = full_name)):
                    found = object_list.filter(last_name__icontains = full_name)
            else:
                found = object_list
        else:
            found = object_list


                
    else:
        found = object_list
        form = ClientBasicFilterForm()
    found = found.order_by('-pk')  
    
    return render(request, 'client/clients.html', {'form':form, 'object_list': found})

class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    permission_required = 'client.delete_client' 
    template_name = "client/client-delete.html"    
    success_url = '/clients'

    def test_func(self):
        return self.request.user.is_staff


class TesterCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Tester
    form_class = TesterForm
    template_name = "tester/tester-form.html"

    def test_func(self):
        return self.request.user.is_staff    

class TesterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Tester
    form_class = TesterForm    
    template_name = "tester/tester-form.html"

    def test_func(self):
        return self.request.user.is_staff


class TesterDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Tester
    template_name = "tester/tester-detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        performed_by = Tester.objects.filter(pk=self.kwargs['pk']).first()
        recent_reports = Report.objects.filter(performed_by__pk=performed_by.pk).order_by('-pk')[:5]
        context['reports'] = recent_reports
        return context

    def test_func(self):
        return self.request.user.is_staff


class TesterListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Tester
    template_name = "tester/testers.html"
    ordering = ['-pk']


    def test_func(self):
        return self.request.user.is_staff


class TesterDeleteView(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, DeleteView):
    model = Tester
    permission_required = 'tester.delete_tester' 
    template_name = "tester/tester-delete.html"
    success_url = '/testers'

    def test_func(self):
        return self.request.user.is_staff


class LabCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Lab
    form_class = LabForm
    template_name = "lab/lab-form.html"


    def test_func(self):
        return self.request.user.is_staff


class LabUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Lab
    form_class = LabForm    
    template_name = "lab/lab-form.html"

    def test_func(self):
        return self.request.user.is_staff    

class LabDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Lab
    template_name = "lab/lab-detail.html"
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        lab = Lab.objects.filter(pk=self.kwargs['pk']).first()
        recent_reports = Report.objects.filter(lab__pk=lab.pk).order_by('-pk')[:5]
        context['reports'] = recent_reports
        return context

    def test_func(self):
        return self.request.user.is_staff


class LabListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Lab
    template_name = "lab/labs.html"
    ordering = ['-pk']


    def test_func(self):
        return self.request.user.is_staff

class LabDeleteView(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, DeleteView):
    model = Lab
    permission_required = 'lab.delete_lab' 
    template_name = "lab/lab-delete.html"
    success_url = '/labs'
    def test_func(self):
        return self.request.user.is_staff


def report_doc(request, pk):
    obj = get_object_or_404(Report, pk=pk)     
    #Retrieve data or whatever you need

    link = request.META['HTTP_HOST'] + request.path
    host = request.META['HTTP_HOST']
    # return render(request, 'report/report-detail-bare.html',
    #         {
    #             'pagesize':'A4',
    #             'object': obj,
    #             'link': link

    #         })
    
    MEDIA_URL = settings.MEDIA_ROOT

    return render_to_pdf(
            'report/report-detail-bare.html',
            {
                'pagesize':'A4',
                'object': obj,
                'request':request,
                'link': link,
                'MEDIA_URL':MEDIA_URL,
                'host': host

            }
        )


def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))

def height(logo, width):
    divisor = logo.width/width
    return logo.height/divisor

def width(logo, height):
    divisor = logo.height/height
    return logo.width/divisor

def gen_qr(text, path):
    qr = qrcode.make(text)
    savedqr = qr.save(path)
    print(savedqr)
    print(qr.get_image())

    return savedqr

def new_pdf_page(request, pk):
    obj = get_object_or_404(Report, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    pdf_name = f"{obj}.pdf"
    response['Content-Disposition'] = f'filename={pdf_name}'
    styles = getSampleStyleSheet()
    heading3 = styles['Heading3']
    heading4 = styles['Heading4']
    heading5 = styles['Heading5']
    heading6 = styles['Heading6']


    buff = io.BytesIO()
    # Doc Size and Margins
    doc = SimpleDocTemplate(buff, pagesize=letter, 
        leftMargin = 2.1 * cm, 
        rightMargin = 2.2 * cm,
        topMargin = 2.5* cm, 
        bottomMargin = 1.5 * cm)


    # Fonts
    font_url = 'reports/static/fonts/FGMRegular/FGMR.ttf'
    bold_font_url = 'reports/static/fonts/FGBold/FGB.ttf'
    bold__italic_font_url = 'reports/static/fonts/FGBoldItalic/FGBI.ttf'
    heavy_bold_font_url = 'reports/static/fonts/FGHB.ttf'
    heavy_italic_font_url = 'reports/static/fonts/FGHeavyItalic/FGHI.ttf'


    pdfmetrics.registerFont(TTFont('FGothic', font_url))
    pdfmetrics.registerFont(TTFont('FGothicBold', bold_font_url))
    pdfmetrics.registerFont(TTFont('FGothicBoldItalic', bold__italic_font_url))
    pdfmetrics.registerFont(TTFont('FGothicHeavyBold', heavy_bold_font_url))
    pdfmetrics.registerFont(TTFont('FGothicHeavyItalic', heavy_italic_font_url))

    Story = []

    # Font Styles
    styles.add(ParagraphStyle(
                        name='style',
                        parent=styles['Normal'],
                        fontName = 'FGothic',
                        fontSize=8,
                        leading = 13
                        ))
    style = styles["style"]

    styles.add(ParagraphStyle(
                        name='fnormal',
                        parent=styles['style'],
                        fontName = 'FGothic',
                        fontSize=8,
                        leading = 11
                        ))

    styles.add(ParagraphStyle(
                        name='small',
                        parent=styles['style'],
                        fontName = 'FGothic',
                        fontSize=7.2,
                        leading = 11
                        ))


    styles.add(ParagraphStyle(
                        name='covid_small',
                        parent=styles['style'],
                        fontName = 'FGothic',
                        fontSize=8,
                        leading = 11
                        ))

    styles.add(ParagraphStyle(
                    name='small_bold',
                    parent=styles['small'],
                    fontName = 'FGothicBold',
                    fontSize=6.2,

                    ))

    styles.add(ParagraphStyle(
                    name='small_heavy_bold',
                    parent=styles['small'],
                    fontName = 'FGothicHeavyBold',
                    fontSize=7.6,

                    ))

    styles.add(ParagraphStyle(
                    name='heavy_bold',
                    parent=styles['small'],
                    fontName = 'FGothicHeavyBold',
                    fontSize=8.4,

                    ))

    styles.add(ParagraphStyle(
                    name='small_bold_italic',
                    parent=styles['small'],
                    fontName = 'FGothicBoldItalic',
                    fontSize=6.2,
                    ))


    styles.add(ParagraphStyle(
                    name='small_heavy_italic',
                    parent=styles['small'],
                    fontName = 'FGothicHeavyItalic',
                    fontSize=7.6,
                    ))


    small = styles['small']
    covid_small = styles['covid_small']
    fnormal = styles['fnormal']
    small_bold = styles['small_bold']
    small_bold_italic = styles['small_bold_italic']
    small_heavy_bold = styles['small_heavy_bold']
    heavy_bold = styles['heavy_bold']
    small_heavy_italic = styles['small_heavy_italic']



    header_width = 22 * cm

    if(obj.lab.header):
        header = pdfImage(obj.lab.header.path, width=header_width, height=height(obj.lab.header, header_width))

    # Story.append(header)
    Story.append(Spacer(1, 1.1*cm))
    data_row_height =  .49*cm

    if(not obj.doctor):
        doctor = ''
    else:
        doctor = obj.doctor     
    patient_data= [
        [Paragraph(f'Order ID: ', heavy_bold), Paragraph(f'{obj.pk}', heavy_bold), '', ''],
        [Paragraph(f'Patient ID: ', fnormal), Paragraph(f'{obj.client.pk}', fnormal), '', ''],
        [Paragraph(f'Patient : ', fnormal), Paragraph(f'{obj.client.full_name}'.upper(), fnormal), '', ''],
        [Paragraph(f'Date of Birth: ', fnormal), Paragraph(f'{obj.client.dob.strftime("%d/%m/%Y")}', fnormal), Paragraph(f'Doc. ID: ', fnormal), Paragraph(f'{obj.doc_id}', fnormal)],
        [Paragraph(f'Age: ', fnormal), Paragraph(f'{obj.client.age}', fnormal), Paragraph(f'Sex: ', fnormal), Paragraph(f'{obj.client.sex[0]}'.upper(), fnormal)],
        [Paragraph(f'Doctor: ', fnormal), Paragraph(f'{doctor}', fnormal), '', ''],
        ]


    if(not obj.order_type):
        order_type = ''
    else:
        order_type = obj.order_type

    if(not obj.insurance):
        insurance = ''
    else:
        insurance = obj.insurance
    if(not obj.company):
        company = ''
    else:
        company = obj.company
    
    report_col1_data= [
        [f'Collected:', '',Paragraph(f'{obj.collect_date.strftime("%d/%m/%Y %I:%M %p")}'.lower(), fnormal)],       
        [f'Print Date:', '',Paragraph(f'{obj.print_date.strftime("%d/%m/%Y %I:%M %p")}'.lower(), fnormal)],
        [f'Branch: ', Paragraph(f'{obj.branch_no}', fnormal),Paragraph(f'{obj.lab.name}'.upper(), fnormal)],
        [f'Order Type:', '', Paragraph(f'{order_type}', fnormal)],
        [f'Insurance: ', '',Paragraph(f'{insurance}', fnormal)],
        [f'Company: ', '',Paragraph(f'{company}', fnormal)],
        ]
    
    report_col_1 = Table(report_col1_data,2*[.8*inch], 6*[data_row_height])
    report_col_1.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])) 
    
   



    # Test Request | 2nd Table
    test_request_data = [[Paragraph('Test Request: ', style=covid_small), Paragraph(f'{obj.test_request}', style=covid_small)]]
    test_request_table= Table(test_request_data,[2.2*cm, 18.1*cm], 1*[.68*cm])
    test_request_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('BOX',(0,0),(1,-1),1.2, colors.black),
        ('SIZE', (0, 0), (-1, -1), 7.2),
        ('FONTNAME', (0,0), (0,-1), 'FGothic'),
        ('LEFTPADDING', (0, 0), (-1, -1), .25 * cm),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))


    patient_table=Table(patient_data,[2.1*cm, 3.65*cm, 1.4*cm, 3*cm
    ], 6*[data_row_height])
    patient_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0,0), (0,-1), 'FGothic'),
        ('LEFTPADDING', (0, 0), (-1, -1), .5),
        ('TOPPADDING', (0, 0), (-1, -1), .5 *cm),
    ]))


    report_col_data = report_col1_data
    report_col= Table(report_col_data,[2.1*cm, .85*cm, 7*cm], 6*[data_row_height])
    report_col.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0,0), (0,-1), 'FGothic'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), .5 *cm),

    ]))


    # Main Table (First)
    data_table_data = [[patient_table, report_col]]
    data_table=Table(data_table_data,[10.3*cm, 10*cm], 1*[3.2*cm])
    data_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('LEADING', (0, 0), (-1, -1), 8.4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
        ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
        ('GRID',(0,0),(1,-1),1.5, colors.black),
    ]))


    Story.append(data_table)
    Story.append(Spacer(1,.6*cm))
    Story.append(test_request_table)
    # Story.append(Spacer(1,.08*cm))


    #
    row_1_data = [['',Paragraph('RESULT(S)', small_heavy_bold), Paragraph('UNIT', small_heavy_bold), Paragraph('REFERENCE VALUES', small_heavy_bold)]]
    row_1_table=Table(row_1_data, [3.57 *cm, 5.8*cm, 2.5 *cm , 1.5*inch], 1*[ .8*cm])
    row_1_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 6.4),
        ('TOPPADDING', (0, 0), (-1, -1), .3*cm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), .5),
    ]))

    Story.append(row_1_table)
    # test_req_pos_data = [[Paragraph(f'{obj.test_request}', heading6), '']]
    test_req_pos_data = [[Paragraph(f'{obj.test_request}', style=small)]]
    test_req_pos_table = Table(test_req_pos_data, 1*[7*cm],1* [.3 * inch])
    test_req_pos_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('FONTNAME', (0,0), (0,-1), 'FGothicBold'),
        
    ]))

    row_2_sub_data = [['',f'{obj.print_date.strftime("%d/%m/%Y %I:%M:%S%p").lower()} DEPARTMENT: {obj.department}', '',f'Prepared by: {obj.performed_by.prepared_by.lower()}']]
    row_2_sub_table = Table(row_2_sub_data, [5.45*cm, 6*cm, 4*cm], 1*[.35*cm])
    row_2_sub_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 6.4),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0,0), (0,-1), 'FGothic'),
    ]))

    row_2_data = [[ Paragraph(f'{obj.test_request}',  style=small_heavy_italic), row_2_sub_table]]
    row_2_table=Table(row_2_data, [2.2*cm, 17.9*cm], 1*[.35*cm])
    row_2_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 6.4),
        ('FONTNAME', (0,0), (0,-1), 'FGothic'),
        ('LINEBELOW', (0, 0), (-1, -1), .8, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

    ]))     
    Story.append(row_2_table)

    safe_attrs = clean.defs.safe_attrs
    cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=frozenset())

    msgStr = obj.details
    msgStr = cleaner.clean_html(msgStr)
    first_p = msgStr.find('<p>')
    if(first_p >= 0):
        msgStr = msgStr[first_p+3:]
    msgStr = msgStr.replace('<br>','<br />')
    msgStr = msgStr.replace('<p>','<br />')
    msgStr = msgStr.replace('</p>','<br />')

    #Result and Details Sub Table
    req_data = [[ Paragraph(f'{obj.result}'.upper(), style=small), Paragraph(f'{msgStr}',  style=small)]]
    req_table = Table(req_data, 1*[8.15*cm, 5.25*cm],1* [.3 * inch])
    req_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0,0), (0,-1), 'FGothic'),


    ]))  

    req_res_data = [[req_table, Paragraph(f'{obj.result}', small), '', '']]
    req_res_table = Table(req_res_data, [4.7*cm, 4.5*cm],1* [.3 * inch])
    req_res_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))  
    row_3_data = [[Paragraph(f'{obj.test_request}', small), req_table,'']]
    row_3_col_1_data = []
    
    row_3_table=Table(row_3_data,[5.7 *cm, 11*cm, 3.5*cm], 1*[2.8*inch])
    row_3_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 6.2),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), .5),
    ])) 
    
    Story.append(row_3_table)
    Story.append(Spacer(1,0.14*inch))
    
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    current_site = get_current_site(request)
    host = f'{protocol}://{current_site.domain}{request.path}'
    path = settings.MEDIA_ROOT + '/qrcodes/'+str(obj.pk)+".png"    
    qrimage = gen_qr(host, path)
    qr_size = 2.5*cm
    qr = pdfImage(path, width=qr_size, height=qr_size)
    if(obj.lab.stamp):
        stamp = pdfImage(obj.lab.stamp.path, width=2.5*inch, height=height(obj.lab.stamp, 2.5*inch))
    bottom_data= [['', qr, stamp]]
    bottom_table=Table(bottom_data, [.3*cm,11.3*cm, 9.5*cm], 1*[5.5*cm])
    bottom_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

    ]))
    
    
    Story.append(Spacer(1,1*inch))
    Story.append(bottom_table)

    signature = pdfImage(obj.performed_by.signature.path, width=2*inch, height=height(obj.performed_by.signature, 2*inch))
    signature_data= [[signature]]
    signature_table=Table(signature_data, 1*[1.8*inch], 1*[.5*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.2, colors.black),

    ]))

    signature = pdfImage(obj.performed_by.signature.path, width=2*inch, height=height(obj.performed_by.signature, 2*inch))
    # signature_title = Paragraph('Laboratory Manager', small)
    signature_title_data= [['Laboratory Manager']]
    signature_title_table=Table(signature_title_data, 1*[1.8*inch], 1*[.3*inch])
    signature_title_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    signature_section_table=Table([
                                    [signature_table],
                                    [signature_title_table]
                                ], 1*[2*inch], 2*[.3*inch])

    # Add the content as before then...
    if(obj.lab.footer):
        footer_width = 21.5 *cm
        footer_height = height(obj.lab.footer, footer_width)
        footer_img = pdfImage(obj.lab.footer.path, width=footer_width, height=footer_height)

    foot_table=Table([
        ['','','',signature_section_table],
        [footer_img, '', '', '']], [2*inch, 2*inch, 5.55*cm, 2*inch], [1*cm, .75*cm ])     
    footer = foot_table
        # Story.append(footer)
    


    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='test', frames=frame, onPage=partial(header_and_footer, header_content=header, footer_content=footer))
    doc.addPageTemplates([template])
    # doc.build([Spacer(1,1*inch)], onFirstPage=myLaterPages, onLaterPages=myLaterPages)
    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    response.write(buff.getvalue())
    buff.close()
    return response


# def pdf_page_old(request, pk):
#     obj = get_object_or_404(Report, pk=pk)
#     # Set up response
#     response = HttpResponse(content_type='application/pdf')
#     pdf_name = f"{obj}.pdf"
#     response['Content-Disposition'] = f'filename={pdf_name}'
#     buff = io.BytesIO()
#     doc = SimpleDocTemplate(buff, title=str(obj))
#     Story = []

#     styles=getSampleStyleSheet()
#     para = styles["Normal"]
#     heading1 = styles['Heading1']  
#     heading3 = styles['Heading3']
#     # Add the content as before then...
#     # host = request.META['HTTP_HOST'] + request.path
#     if request.is_secure():
#         protocol = 'https'
#     else:
#         protocol = 'http'

#     current_site = get_current_site(request)


#     logo_width = 1*inch
#     logo_height = height(obj.lab.logo, logo_width)
#     im = pdfImage(obj.lab.logo.path, width=logo_width, height=logo_height)
#     im.hAlign='RIGHT'
#     host = f'{protocol}://{current_site.domain}{request.path}'
#     path = settings.MEDIA_ROOT + '/qrcodes/'+str(obj.pk)+".png"    
#     qrimage = gen_qr(host, path)
#     qr = pdfImage(path, width=1.5*inch, height=1.5*inch)
#     f1Story = []
#     f2Story = []
    

    
#     # Story.append(qr)
    


#     # Two Columns
#     frame1 = Frame( 
#                     .5*inch, 
#                     inch*10.5, 
#                     4*inch, 
#                     .5*inch, 
#                     showBoundary=0)
#     Story.append(Paragraph(obj.client.full_name, heading1))
    
#     frame2 = Frame( 
#                     4.5*inch, 
#                     (inch*10.6)-logo_height, 
#                     3*inch, 
#                     logo_height+(.5 * inch), 
#                     showBoundary=0)
#     Story.append(im)

#     meta_data_frame = Frame( 
#                     .5*inch, 
#                     inch*9.5, 
#                     6*inch, 
#                     1*inch, 
#                     showBoundary=0)
#     meta_data= [[f'DOB: {obj.client.dob}', f'ID Number: {obj.client.id_number}',  f'Test Date: {obj.date.strftime("%Y-%m-%d %H:%M:%S")}', f'Test ID: {obj.pk}']]
#     meta_data_table=Table(meta_data,4*[1.5*inch], 1*[0.5*inch])
#     meta_data_table.setStyle(TableStyle([

#         ('ALIGN', (0, 0), (1, -1), 'LEFT'),
#         ('SIZE', (0, 0), (-1, -1), 7),
#         ('LEADING', (0, 0), (-1, -1), 8.4),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('TOPPADDING', (0, 0), (-1, -1), 2.6),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
#         ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.gray),
#     ]))
#     Story.append(meta_data_table)
    
#     type_frame = Frame( 
#                     .5*inch, 
#                     inch*9.4, 
#                     4*inch, 
#                     .5*inch, 
#                     showBoundary=0)

#     Story.append(Paragraph(obj.type, heading3))

#     result_frame = Frame( 
#                 .5*inch, 
#                 inch*9, 
#                 4*inch, 
#                 .6*inch, 
#                 showBoundary=0)
#     result_data= [[f'Desired Result: {obj.desired_result}', f'Result: {obj.result}']]
#     result_table=Table(result_data,2*[2*inch], 1*[.4*inch])
#     result_table.setStyle(TableStyle([
#         ('ALIGN', (0, 0), (1, -1), 'LEFT'),
#         ('SIZE', (0, 0), (-1, -1), 10),
#         ('LEADING', (0, 0), (-1, -1), 8.4),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('TOPPADDING', (0, 0), (-1, -1), 2.6),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
#     ]))
#     Story.append(result_table)
    
#     pre_footer_frame = Frame( 
#                     .5*inch, 
#                     inch*2.5, 
#                     7.5*inch, 
#                     1*inch, 
#                     showBoundary=0)
#     pre_footer_data= [[qr,  f'Performed By: {obj.performed_by.full_name}']]
#     pre_footer_table=Table(pre_footer_data,2*[3.5*inch], 1*[0.8*inch])
#     pre_footer_table.setStyle(TableStyle([
#         ('ALIGN', (0, 0), (1, -1), 'LEFT'),
#         ('SIZE', (0, 0), (-1, -1), 14),
#         ('LEADING', (0, 0), (-1, -1), 8.4),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('TOPPADDING', (0, 0), (-1, -1), 2.6),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
#     ]))
#     Story.append(pre_footer_table)

#     details_frame = Frame( 
#                 .5*inch, 
#                 inch*4, 
#                 7.5*inch, 
#                 4*inch, 
#                 showBoundary=0)
#     Story.append(Paragraph(obj.details, para))

    

#     frame10 = Frame(
#                     ((doc.width/2) + (inch*1.5)), 
#                     inch*9, 
#                     doc.width/2, 
#                     inch*2, id='col2', 
#                     showBoundary=1)
#     # frame1.addFromList(f1Story)
#     template = PageTemplate(id='TwoBoxKeystroke', frames=[frame1, frame2, meta_data_frame, type_frame, result_frame, pre_footer_frame, details_frame])
#     doc.addPageTemplates([template])
    
#     doc.build(Story, onFirstPage=myLaterPages, onLaterPages=myLaterPages)

#     response.write(buff.getvalue())
#     buff.close()
#     return response
