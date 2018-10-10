from django.contrib import admin
from django.urls import path, re_path, include

from VersionInfoApp import views

urlpatterns = [
    re_path('^version$', views.show_versioninfo),
]
