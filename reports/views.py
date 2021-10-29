from django.shortcuts import render
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reports.pdf import render_to_pdf
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
from reportlab.lib import utils
import qrcode


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

class ReportDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Report
    permission_required = 'report.delete_report' 
    template_name = "report/report-delete.html"

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "client/client-form.html"

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm    
    template_name = "client/client-form.html"

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "client/client-detail.html"

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "client/clients.html"

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

class TesterListView(LoginRequiredMixin, ListView):
    model = Tester
    template_name = "tester/testers.html"

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

class LabListView(LoginRequiredMixin, ListView):
    model = Lab
    template_name = "lab/labs.html"

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

def some_view(request, pk):
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
    logo_size = 50
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