# 使用celery
from celery import Celery

# 创建一个Celery类的实例对象
from django.core.mail import send_mail

from WorkHome import settings

# 在任务处理者端加这几句
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WorkHome.settings')
django.setup()

app = Celery('celery_tasks.tasks', broker=settings.REDIS_CELERY_HOME if settings.ISHOME else settings.REDIS_CELERY_COMP)


# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    # 发邮件
    subject = '天天生鲜欢迎信息'
    message = ''
    html_msg = '<h1>%s</h1><a href="http://127.0.0.1:8000/user/active/%s">hhh</a>' % (username, token)
    sender = settings.EMAIL_FROM
    reciver = [to_email]
    send_mail(subject, message, sender, reciver, html_message=html_msg)
