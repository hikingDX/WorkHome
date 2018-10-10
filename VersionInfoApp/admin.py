from django.contrib import admin

# Register your models here.
# 后台管理相关文件
# 自定义模型管理类
from VersionInfoApp.models import VersionInfo, BugInfo


class VersionInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'vtitle', 'vcommit_date']


class BugInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'bcontent', 'bsolution']


# Register your models here.
# 注册模型类
admin.site.register(VersionInfo, VersionInfoAdmin)
admin.site.register(BugInfo, BugInfoAdmin)
