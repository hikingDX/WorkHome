from django.urls import re_path

from apps.goods import views

app_name = 'goods'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
]
