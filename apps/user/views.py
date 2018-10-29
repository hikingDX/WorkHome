import re

from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic.base import View

from WorkHome import settings
from apps.user.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.core.mail import send_mail

from celery_tasks.tasks import send_register_active_email


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        # 1.接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 2.进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 邮箱匹配
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 3.进行业务处理:
        # user = User()
        # user.username = username
        # user.password = password
        # user.save()
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 4.返回应答

        return redirect(reverse('goods:index'))


class RegisterView(View):
    # 注册
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 1.接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 2.进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 邮箱匹配
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 3.进行业务处理:
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        # 发送激活邮件,包含激活链接: /user/active/
        # 激活链接中需要包含用户的身份信息:并且要把身份信息进行加密
        # 加密用户的身份信息，生成激活的token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode()
        # # 发邮件
        # subject = '天天生鲜欢迎信息'
        # message = ''
        # html_msg = '<a href="http://127.0.0.1:8000/user/active/%s">hhh</a>' % (token)
        # sender = settings.EMAIL_FROM
        # reciver = [email]
        # send_mail(subject, message, sender, reciver, html_message=html_msg)
        send_register_active_email.delay(email, user.username, token)
        # 4.返回应答
        return redirect(reverse('goods:index'))


class ActiveView(View):
    # 用户激活
    def get(self, request, token):
        # 进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活的用户id
            user_id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转到登录页面
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # 校验数据
        if not all(username,password):
            return  render(request,'login.html',{'errmsg':'数据不完整'})
        # 业务逻辑
        User.objects.get(username = username,password =password)




