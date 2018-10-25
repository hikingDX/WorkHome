from django.urls import path, re_path, include
from apps.user import views
from apps.user.views import RegisterView, ActiveView, LoginView

app_name = 'user'
urlpatterns = [
    # re_path(r'^register$', views.register, name='register'),
    # re_path(r'^register_handle$', views.register_handle, name='register_handle'),  # 注册处理
    re_path(r'^register$', RegisterView.as_view(), name='register'),
    re_path(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),  # 用户激活
    re_path(r'^login$', LoginView.as_view(), name='login'),
]
