from django.shortcuts import HttpResponse, render
import tempfile

import qr_app.qrmap as qrmap
from .forms import CreateQRForm


# Create your views here.
def index(request):
    context = {}
    return render(request, 'qr_app/index.html', context)


def qr_template(request):
    if 'version' not in request.GET:
        return HttpResponse('Include a version')
    try:
        version = int(request.GET['version'])
    except ValueError:
        return HttpResponse('version should be an integer')
    if version < 1 or version > 40:
        return HttpResponse('version should be between 1 and 40')

    qr_map = qrmap.get_qr_map(version, 'alphanumeric', 'L')
    filename = '/tmp/' + next(tempfile._get_candidate_names()) + '.png'
    qr_map.save(filename)

    try:
        with open(filename, "rb") as f:
            return HttpResponse(f.read(), content_type="image/png")
    except IOError:
        return HttpResponse(f'Error creating QR template')


def get_temp_name():
    return '/tmp/' + next(tempfile._get_candidate_names()) + '.png'


def save_file(f):
    filename = get_temp_name()
    with open(filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return filename


def create_qr(request):
    if request.method == 'POST':
        form = CreateQRForm(request.POST, request.FILES)
        if True:#form.is_valid():
            qrdesign = request.FILES.get('qrdesign', None)
            filename = save_file(qrdesign)
            qr = qrmap.create_qr_from_design(
                filename, 'HTTPS://MY-QR.ART/R', 'alphanumeric', 'L')

            qrfile = get_temp_name()
            qr.png(qrfile, scale=5)
            with open(qrfile, "rb") as f:
                return HttpResponse(f.read(), content_type="image/png")
        else:
            return HttpResponse('Form invalid')
    else:
        return HttpResponse('Only accessible as POST')
