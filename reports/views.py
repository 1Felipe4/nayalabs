from datetime import datetime
from functools import partial
from django.http.response import HttpResponse
from django.shortcuts import render
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.tables import Table, TableStyle
from reports.pdf import render_to_pdf
from reports.pdf_template import PAGESIZE, header_and_footer, myFirstPage, myLaterPages
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
from reportlab.lib.styles import getSampleStyleSheet
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

# def pdf_view(request, pk):
#     # Create a file-like buffer to receive PDF data.
#     buffer = io.BytesIO()
#     obj = get_object_or_404(Report, pk=pk)     

#     # Create the PDF object, using the buffer as its "file."
#     p = canvas.Canvas(buffer)
#     img = Image.open(obj.lab.logo)
#     logo = ImageReader(img)
#     host = request.META['HTTP_HOST'] + request.path
#     qr = qrcode.make(host)
#     savedqr = qr.save('qr.png')
#     qrimage = qr.get_image()
#     print(qrimage)
#     print(ImageReader(qrimage))
#     drawqr = ImageReader(qrimage)
#     logo_size = 2*inch
#     barcode_size = 75

#     # Draw things on the PDF. Here's where the PDF generation happens.
#     # See the ReportLab documentation for the full list of functionality.
#     p.drawString(100, 100, host)
#     p.drawImage(logo, 10, 10, mask='auto', height=height(obj.lab.logo, logo_size), width=logo_size)
#     p.drawImage(drawqr, 200, 10, mask='auto', height=height(qrimage, barcode_size), width=barcode_size)
#     # Close the PDF object cleanly, and we're done.
#     p.showPage()
#     p.save()

#     # FileResponse sets the Content-Disposition header so that browsers
#     # present the option to save the file.
#     buffer.seek(0)
#     return FileResponse(buffer, as_attachment=False, filename='hello.pdf')

def pdf_page(request, pk):
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
    doc = SimpleDocTemplate(buff, pagesize=letter, 
        leftMargin = 2.2 * cm, 
        rightMargin = 2.2 * cm,
        topMargin = 2.5* cm, 
        bottomMargin = 1.5 * cm)

    font_url = 'reports/static/fonts/FGMRegular/FGMR.ttf'
    bold_font_url = 'reports/static/fonts/FGBold/FGB.ttf'

    pdfmetrics.registerFont(TTFont('FGothic', font_url))

    Story = []
    style = styles["Normal"]
    style.leading = 24
    style.weight = '900'
    small = styles["Normal"]
    small.weight = '900'
    small.fontName = 'FGothic'
    small.fontSize = 8
    style.leading = 13
    header_width = 22 * cm

    if(obj.lab.header):
        header = pdfImage(obj.lab.header.path, width=header_width, height=height(obj.lab.header, header_width))

        # Story.append(header)
    Story.append(Spacer(1, 1.1*cm))
    data_row_height =  .52*cm

    doc_id_data = [[Paragraph(f'Doc. ID: ', small), Paragraph(f'{obj.doc_id}', small)]]
    doc_id_table=Table(doc_id_data, 2*[.6*inch], 1*[data_row_height])

    sex_data = [[Paragraph(f'Sex: ', small), Paragraph(f'{obj.client.sex[0]}'.upper(), small)]]

    sex_table=Table(sex_data, 2*[.6*inch], 1*[data_row_height])


    patient_data= [
        [Paragraph(f'Order ID: ', small), Paragraph(f'{obj.pk}', small), ''],
        [Paragraph(f'Patient ID: ', small), Paragraph(f'{obj.client.pk}', small), ''],
        [Paragraph(f'Patient: ', small), Paragraph(f'{obj.client.full_name}'.upper(), small), ''],
        [Paragraph(f'Date of Birth: ', small), Paragraph(f'{obj.client.dob}', small), doc_id_table],
        [Paragraph(f'Age: ', small), Paragraph(f'{obj.client.age}', small), sex_table],
        [Paragraph(f'Doctor: ', small), Paragraph(f'{obj.doctor}', small)],
        ]


    report_col1_data= [
        [Paragraph(f'Collected:', small), ''],       
        [Paragraph(f'Print Date:', small), ''],
        [Paragraph(f'Branch: ', small), Paragraph(f'{obj.branch_no}', small)],
        [Paragraph(f'Order Type: ', small), ''],
        [Paragraph(f'Insurance: ', small), ''],
        [Paragraph(f'Company:', small), ''],
        ]
    
    report_col_1 = Table(report_col1_data,2*[.8*inch], 6*[data_row_height])
    report_col_1.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])) 
    
    report_col2_data= [
        [Paragraph(f'{obj.collect_date.strftime("%d/%m/%Y %I:%M %p")}', small)],       
        [Paragraph(f'{obj.print_date.strftime("%d/%m/%Y %I:%M %p")}', small)],
        [Paragraph(f'{obj.lab.name}', small)],
        [Paragraph(f'{obj.order_type}', small)],
        [Paragraph(f'{obj.insurance}', small)],
        [Paragraph(f'{obj.company}', small)],
        ]



    report_col_2 = Table(report_col2_data,1*[5*cm], 6*[data_row_height])
    report_col_2.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))       
    report_col_data= [[report_col_1, report_col_2]]
    report_col= Table(report_col_data,2*[3.4*cm], 1*[1.3*inch])
    report_col.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), .5),

    ]))

    report_table_data= [[patient_data, report_col]]
    test_request_data= [[Paragraph('Test Request: ', small), Paragraph(f'{obj.test_request}', small)]]
    test_request_table = Table(test_request_data, 2*[1.5*inch], 1*[data_row_height])
    test_request_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    test_request_outer_data= [[test_request_table, '']]
    test_request_outer_table= Table(test_request_outer_data,2*[10.1*cm], 1*[.28*inch])
    test_request_outer_table.setStyle(TableStyle([
        ('BOX',(0,0),(1,-1),1.5, colors.black),
    ]))

    patient_sub_table = Table(patient_data,3*[1.2*inch], 6*[data_row_height])
    patient_sub_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    patient_table=Table([[patient_sub_table]], 1*[10.1*cm], 1*[3.4*cm])
    patient_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), .5),
    ]))
    report_table=Table(report_table_data,2*[3.6*inch], 1*[2.8*inch])

    data_table_data = [[patient_table, report_col]]
    data_table=Table(data_table_data,2*[10.1*cm], 1*[3.3*cm])
    data_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('LEADING', (0, 0), (-1, -1), 8.4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
        ('LEFTPADDING', (0, 0), (-1, -1), .5),
        ('GRID',(0,0),(1,-1),1.5, colors.black),
    ]))

    Story.append(data_table)
    Story.append(Spacer(1,.5*cm))
    Story.append(test_request_outer_table)


    #
    row_1_data = [['',Paragraph('RESULT(S)', heading6), Paragraph('UNIT', heading6), Paragraph('REFERENCE VALUES', heading6)]]
    row_1_table=Table(row_1_data, 4*[1.5*inch], 1*[.30*inch])
    row_1_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 6.4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    Story.append(row_1_table)
    # test_req_pos_data = [[Paragraph(f'{obj.test_request}', heading6), '']]
    test_req_pos_data = [[f'{obj.test_request}']]
    test_req_pos_table = Table(test_req_pos_data, 1*[2.2*inch],1* [.3 * inch])
    test_req_pos_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold')
        
    ]))    
    row_2_data = [[ test_req_pos_table, '', f'{obj.unit_date.strftime("%d/%m/%Y %I:%M:%S%p")}', f'Department: {obj.department}', f'Prepared by: {obj.performed_by.prepared_by}']]
    row_2_table=Table(row_2_data, 5*[4.04*cm], 1*[.30*inch])

    row_2_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'RIGHT'),
        ('SIZE', (0, 0), (-1, -1), 7),
        ('LINEBELOW', (0, 0), (-1, -1), 0.2, colors.gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
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

    req_data = [[f'{obj.test_request}']]
    req_table = Table(req_data, 1*[2.2*inch],1* [.3 * inch])
    req_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

        
    ]))  

    req_res_data = [[req_table, Paragraph(f'{obj.result}', small), '', '']]
    req_res_table = Table(req_res_data, 2*[1.8*inch],1* [.3 * inch])
    req_res_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))  
    row_3_data = [[ req_res_table, '',Paragraph(f'{msgStr}', small)]]
    row_3_col_1_data = []
    
    row_3_table=Table(row_3_data,3*[2.25*inch], 1*[3*inch])
    row_3_table.setStyle(TableStyle([
        ('SIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), .5),
    ])) 
    
    Story.append(row_3_table)
    Story.append(Spacer(1,0.2*inch))
    
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    current_site = get_current_site(request)
    host = f'{protocol}://{current_site.domain}{request.path}'
    path = settings.MEDIA_ROOT + '/qrcodes/'+str(obj.pk)+".png"    
    qrimage = gen_qr(host, path)
    qr = pdfImage(path, width=1*inch, height=1*inch)
    if(obj.lab.stamp):
        stamp = pdfImage(obj.lab.stamp.path, width=2.5*inch, height=height(obj.lab.stamp, 2.5*inch))
    bottom_data= [[qr,'','', stamp,'','']]
    bottom_table=Table(bottom_data, 6*[1.3*inch], 1*[2*inch])
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

    foot_table=Table([['','','',signature_section_table]], 4*[2*inch], 1*[1*inch])
    foot_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 0.2, colors.black),

    ]))         
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
