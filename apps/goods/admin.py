from django.contrib import admin
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner, GoodsImage, \
    Goods, GoodsSKU

# Register your models here.
admin.site.register(GoodsType)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(IndexPromotionBanner)
admin.site.register(GoodsImage)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
