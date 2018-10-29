import re

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic.base import View
from django_redis import get_redis_connection

from WorkHome import settings
from apps.goods.models import GoodsSKU
from apps.user.models import User, Address
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.core.mail import send_mail
from utils.mixin import LoginRequiredMixin

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
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})
        # 业务逻辑
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 记录用户的登录状态
                login(request, user)
                # 获取登录后所要跳转的地址
                # 默认跳转到首页
                # 如果是require_login返回的url：http://127.0.0.1:8000/user/login?next=/user/
                # 有一个登录成功后要跳转的页面，k:next v:/user/
                next_url = request.GET.get('next', reverse('goods:index'))  # 第二个参数是默认值
                # 跳转到next_url
                response = redirect(next_url)
                # 判断是否记住用户名
                remember = request.POST.get('remember')

                if remember == 'on':
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')
                # 返回response
                return response
            else:
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            return render(request, 'login.html', {'errmsg': '用户密码错误'})


class LogoutView(View):
    def get(self, request):
        # 清除用户的session信息
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # page = 'user'
        # request.user.is_authenticated()
        # Django会给request对象添加一个属性request.user
        # 如果未登录返回一个
        # 除了你给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取最近浏览信息
        # 原生方法获取redis链接
        # from redis import StrictRedis
        # StrictRedis(host='' )
        con = get_redis_connection('default')
        history_key = 'history_%d' % user.id
        # 获取用户最近浏览前5个商品id
        sku_ids = con.lrange(history_key, 0, 4)
        # 从数据库中查询用户浏览的具体信息
        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        # 组织上下文
        context = {'page': 'user', 'addresss': address, 'goods_li': goods_li}

        return render(request, 'user_center_info.html', context)


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    def get(self, request):
        # page = 'order'
        return render(request, 'user_center_order.html', {'page': 'order'})


# /user/address
class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        # page='address'
        address = Address.objects.get_default_address(request.user)
        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录用户对应User对象
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default = True
        # 业务处理：地址添加
        Address.objects.create(user=user, receiver=receiver,
                               addr=addr, zip_code=zip_code,
                               phone=phone, is_default=is_default)

        # 返回应答，刷新地址页面
        return redirect(reverse('user:address'))  # get请求方式
