from django.shortcuts import render

# Create your views here.
from VersionInfoApp.models import VersionInfo


def show_versioninfo(request):
    versions = VersionInfo.objects.all()
    data = []
    for version in versions:
        bugs = version.buginfo_set.all()
        data.append({'version': version, 'bugs': bugs})

    return render(request, 'versioninfo/showversion.html', {'data': data})
