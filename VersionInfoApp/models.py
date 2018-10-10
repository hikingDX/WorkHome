from django.db import models


# Create your models here.
class VersionInfo(models.Model):
    vtitle = models.CharField(max_length=200)  # 标题
    vtrader_code = models.CharField(max_length=20)  # 券商代码
    vcommit_date = models.DateField()  # 提交日期
    vname = models.CharField(max_length=100)  # 项目名称描述
    visdebug = models.BooleanField()  # 测试环境
    vserver_ip = models.CharField(max_length=100)  # 认证地址
    vsvn_version = models.CharField(max_length=20)  # svnRevison
    vupdate_address = models.CharField(max_length=100)  # 下载地址
    vversion_code = models.CharField(max_length=20)  # versioncode
    vupadete_version = models.CharField(max_length=200)  # 提交版本
    vbundle_id = models.CharField(max_length=200)  # bundleid

    def __str__(self):
        return self.vtitle


class BugInfo(models.Model):
    bcontent = models.TextField(max_length=200)  # 问题描述
    blevel = models.IntegerField()  # 等级
    bsolution = models.TextField(max_length=200)  # 解决方案
    bresult = models.TextField(max_length=50)  # 自测结果
    bman = models.TextField(max_length=50)  # 负责人
    bversioninfo = models.ForeignKey('VersionInfo', on_delete=models.CASCADE)

    def __str__(self):
        return self.bcontent
