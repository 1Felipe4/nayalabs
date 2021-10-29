from io import BytesIO, StringIO
import os
from django.conf import settings
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from html import escape

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL     # Typically /static/
    #static Root
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path


def render_to_pdf(template_src, context_dict):
    """
    renders a document to pdf using a template
    """
    if context_dict is None:
        context_dict = {}
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result,
                            encoding='UTF-8',link_callback=link_callback)
    if not pdf.err:
        response = HttpResponse(result.getvalue(),
                                 content_type='application/pdf')

        response['Content-Disposition'] = 'filename=report.pdf'

        return response
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def generate(self, template, context, upload=True):
        html = template.render(context)
        pdf_file_object = BytesIO()
        pdf = pisa.pisaDocument(
            src=BytesIO(html.encode("UTF-8")),
            dest=pdf_file_object,
            encoding='UTF-8'        )

        if not pdf.err:
            if upload:
                self.upload(
                    pdf_file_object=pdf_file_object,
                    filename=context['filename']
                )

        return pdf_file_object 