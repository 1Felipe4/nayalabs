import os
from django.conf import settings
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.doctemplate import PageTemplate
from PIL import Image, ImageDraw
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib.units import cm
from reportlab.platypus.frames import Frame
from reportlab.lib import pagesizes
from reportlab.platypus.paragraph import Paragraph
from functools import partial
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as pdfImage
defaultPageSize = letter
PAGE_HEIGHT=defaultPageSize[0]
PAGE_WIDTH=defaultPageSize[0]


def height(img, width):
    divisor = img.width/width
    return img.height/divisor

def header(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.topMargin)
    content.drawOn(canvas, (0 * cm) , (doc.height + doc.bottomMargin) - (.8 * cm)) #doc.height + doc.bottomMargin + doc.topMargin - h)
    # path = os.path.join(settings.STATIC_ROOT,'media\\template_ref.png')
    # print(settings.STATIC_ROOT)
    # img = Image.open(path)
    # draw_img = ImageReader(img)
    # # Draw PDF Page Reference
    # img_width = 21.5*cm
    # canvas.drawImage(draw_img, 0, 0, img_width, height(img, img_width))

    canvas.restoreState()

def footer(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.bottomMargin)
    content.drawOn(canvas, -.2 *cm, .25*cm)
    canvas.restoreState()

def header_and_footer(canvas, doc, header_content, footer_content):
    header(canvas, doc, header_content)
    footer(canvas, doc, footer_content)

styles = getSampleStyleSheet()

filename = "out.pdf"

PAGESIZE = pagesizes.portrait(pagesizes.A4)

pdf = SimpleDocTemplate(filename, pagesize=letter, 
        leftMargin = 2.2 * cm, 
        rightMargin = 2.2 * cm,
        topMargin = 1.5 * cm, 
        bottomMargin = 1.5 * cm)

frame = Frame(pdf.leftMargin, pdf.bottomMargin, pdf.width, pdf.height, id='normal')

header_content = Paragraph("This is a header. testing testing testing  ", styles['Normal'])
footer_content = Paragraph("This is a footer. It goes on every page.  ", styles['Normal'])

template = PageTemplate(id='test', frames=frame, onPage=partial(header_and_footer, header_content=header_content, footer_content=footer_content))

pdf.addPageTemplates([template])

pdf.build([Paragraph("This is content")])


Title = "Lab Report"
pageinfo = "Lab Report"
def myFirstPage(canvas, doc):
    print('hereee')
    canvas.saveState()
    canvas.setFont('Times-Bold',16)
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo)
    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()
    # Create the PDF object, using the buffer as its "file."
    # img = Image.open(settings.STATIC_ROOT+'media/template_ref.png')
    # draw_img = ImageReader(img)
    
    # canvas.drawImage(draw_img)
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))

    canvas.restoreState()

def go():
    doc = SimpleDocTemplate("phello.pdf")
    Story = [Spacer(1,2*inch)]
    style = styles["Normal"]
    for i in range(100):
        bogustext = ("This is Paragraph number %s. " % i) *20
        p = Paragraph(bogustext, style)
        Story.append(p)
        Story.append(Spacer(1,0.2*inch))
    doc.build(Story, onFirstPage=myLaterPages, onLaterPages=myLaterPages)
