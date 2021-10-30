from django.http.response import HttpResponse
from django.shortcuts import render
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.tables import Table, TableStyle
from reports.pdf import render_to_pdf
from reports.pdf_template import myLaterPages
from .forms import ClientForm, LabForm, ReportForm, TesterForm, UserRegisterForm
from .models import Client, Lab, Report, Tester
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView,
    UpdateView,
    DeleteView
    )
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
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

def home(request):
    return redirect('dashboard')

@login_required
def dashboard(request):
    return render(request, 'report/dashboard.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserRegisterForm()

# Create your views here.
class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = "report/report-form.html"
    

class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = Report
    form_class = ReportForm    
    template_name = "report/report-form.html"

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = "report/report-detail.html"

class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = "report/reports.html"
    ordering = ['-pk']


class ReportDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Report
    permission_required = 'report.delete_report' 
    template_name = "report/report-delete.html"

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "client/client-form.html"

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

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm    
    template_name = "client/client-form.html"

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "client/client-detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        client = Client.objects.filter(pk=self.kwargs['pk']).first()
        recent_reports = Report.objects.filter(client__pk=client.pk).order_by('-pk')[:5]
        context['reports'] = recent_reports
        return context

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "client/clients.html"
    ordering = ['-pk']


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    permission_required = 'client.delete_client' 
    template_name = "client/client-delete.html"    

class TesterCreateView(LoginRequiredMixin, CreateView):
    model = Tester
    form_class = TesterForm
    template_name = "tester/tester-form.html"
    

class TesterUpdateView(LoginRequiredMixin, UpdateView):
    model = Tester
    form_class = TesterForm    
    template_name = "tester/tester-form.html"

class TesterDetailView(LoginRequiredMixin, DetailView):
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

class TesterListView(LoginRequiredMixin, ListView):
    model = Tester
    template_name = "tester/testers.html"
    ordering = ['-pk']

class TesterDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Tester
    permission_required = 'tester.delete_tester' 
    template_name = "tester/tester-delete.html"

class LabCreateView(LoginRequiredMixin, CreateView):
    model = Lab
    form_class = LabForm
    template_name = "lab/lab-form.html"

class LabUpdateView(LoginRequiredMixin, UpdateView):
    model = Lab
    form_class = LabForm    
    template_name = "lab/lab-form.html"

class LabDetailView(LoginRequiredMixin, DetailView):
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

class LabListView(LoginRequiredMixin, ListView):
    model = Lab
    template_name = "lab/labs.html"
    ordering = ['-pk']


class LabDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Lab
    permission_required = 'lab.delete_lab' 
    template_name = "lab/lab-delete.html"

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


def gen_qr(text, path):
    qr = qrcode.make(text)
    savedqr = qr.save(path)
    print(savedqr)
    print(qr.get_image())

    return savedqr

def pdf_view(request, pk):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    obj = get_object_or_404(Report, pk=pk)     

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    img = Image.open(obj.lab.logo)
    logo = ImageReader(img)
    host = request.META['HTTP_HOST'] + request.path
    qr = qrcode.make(host)
    savedqr = qr.save('qr.png')
    qrimage = qr.get_image()
    print(qrimage)
    print(ImageReader(qrimage))
    drawqr = ImageReader(qrimage)
    logo_size = 2*inch
    barcode_size = 75

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, host)
    p.drawImage(logo, 10, 10, mask='auto', height=height(obj.lab.logo, logo_size), width=logo_size)
    p.drawImage(drawqr, 200, 10, mask='auto', height=height(qrimage, barcode_size), width=barcode_size)
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename='hello.pdf')

def pdf_page(request, pk):
    PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
    styles = getSampleStyleSheet()

    buff = io.BytesIO()
    doc = SimpleDocTemplate(buff)
    Story = [Spacer(1,2*inch)]
    style = styles["Normal"]

    # Add the content as before then...

    for i in range(100):
        bogustext = ("This is Paragraph number %s. " % i) *20
        p = Paragraph(bogustext, style)
        Story.append(p)
        Story.append(Spacer(1,0.2*inch))
    doc.build(Story, onFirstPage=myLaterPages, onLaterPages=myLaterPages)

    return FileResponse(buff, as_attachment=False, filename='test.pdf',)

def pdf_page_old(request, pk):
    obj = get_object_or_404(Report, pk=pk)
    # Set up response
    response = HttpResponse(content_type='application/pdf')
    pdf_name = f"{obj}.pdf"
    response['Content-Disposition'] = f'filename={pdf_name}'
    buff = io.BytesIO()
    doc = SimpleDocTemplate(buff, title=str(obj))
    Story = []

    styles=getSampleStyleSheet()
    para = styles["Normal"]
    heading1 = styles['Heading1']  
    heading3 = styles['Heading3']
    # Add the content as before then...
    # host = request.META['HTTP_HOST'] + request.path
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'

    current_site = get_current_site(request)

    host = f'{protocol}://{current_site.domain}{request.path}'

    path = settings.MEDIA_ROOT + '/qrcodes/'+str(obj.pk)+".png"
    logo_width = 1*inch
    logo_height = height(obj.lab.logo, logo_width)
    im = pdfImage(obj.lab.logo.path, width=logo_width, height=logo_height)
    im.hAlign='RIGHT'
    qrimage = gen_qr(host, path)
    qr = pdfImage(path, width=1.5*inch, height=1.5*inch)
    f1Story = []
    f2Story = []
    

    
    # Story.append(qr)
    


    # Two Columns
    frame1 = Frame( 
                    .5*inch, 
                    inch*10.5, 
                    4*inch, 
                    .5*inch, 
                    showBoundary=0)
    Story.append(Paragraph(obj.client.full_name, heading1))
    
    frame2 = Frame( 
                    4.5*inch, 
                    (inch*10.6)-logo_height, 
                    3*inch, 
                    logo_height+(.5 * inch), 
                    showBoundary=0)
    Story.append(im)

    meta_data_frame = Frame( 
                    .5*inch, 
                    inch*9.5, 
                    6*inch, 
                    1*inch, 
                    showBoundary=0)
    meta_data= [[f'DOB: {obj.client.dob}', f'ID Number: {obj.client.id_number}',  f'Test Date: {obj.date.strftime("%Y-%m-%d %H:%M:%S")}', f'Test ID: {obj.pk}']]
    meta_data_table=Table(meta_data,4*[1.5*inch], 1*[0.5*inch])
    meta_data_table.setStyle(TableStyle([

        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('SIZE', (0, 0), (-1, -1), 7),
        ('LEADING', (0, 0), (-1, -1), 8.4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.gray),
    ]))
    Story.append(meta_data_table)
    
    type_frame = Frame( 
                    .5*inch, 
                    inch*9.4, 
                    4*inch, 
                    .5*inch, 
                    showBoundary=0)

    Story.append(Paragraph(obj.type, heading3))

    result_frame = Frame( 
                .5*inch, 
                inch*9, 
                4*inch, 
                .6*inch, 
                showBoundary=0)
    result_data= [[f'Desired Result: {obj.desired_result}', f'Result: {obj.result}']]
    result_table=Table(result_data,2*[2*inch], 1*[.4*inch])
    result_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('SIZE', (0, 0), (-1, -1), 10),
        ('LEADING', (0, 0), (-1, -1), 8.4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
    ]))
    Story.append(result_table)
    
    pre_footer_frame = Frame( 
                    .5*inch, 
                    inch*2.5, 
                    7.5*inch, 
                    1*inch, 
                    showBoundary=0)
    pre_footer_data= [[qr,  f'Performed By: {obj.performed_by.full_name}']]
    pre_footer_table=Table(pre_footer_data,2*[3.5*inch], 1*[0.8*inch])
    pre_footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('SIZE', (0, 0), (-1, -1), 14),
        ('LEADING', (0, 0), (-1, -1), 8.4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.6),
    ]))
    Story.append(pre_footer_table)

    details_frame = Frame( 
                .5*inch, 
                inch*4, 
                7.5*inch, 
                4*inch, 
                showBoundary=0)
    Story.append(Paragraph(obj.details, para))

    

    frame10 = Frame(
                    ((doc.width/2) + (inch*1.5)), 
                    inch*9, 
                    doc.width/2, 
                    inch*2, id='col2', 
                    showBoundary=1)
    # frame1.addFromList(f1Story)
    template = PageTemplate(id='TwoBoxKeystroke', frames=[frame1, frame2, meta_data_frame, type_frame, result_frame, pre_footer_frame, details_frame])
    doc.addPageTemplates([template])
    
    doc.build(Story, onFirstPage=myLaterPages, onLaterPages=myLaterPages)

    response.write(buff.getvalue())
    buff.close()
    return response
