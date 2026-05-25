from django.db import models


class Fish(models.Model):
    """鱼类"""
    name = models.CharField('名称（种类）', unique=True, max_length=100, blank=True, null=True)
    name_en = models.CharField('英文名', max_length=200, blank=True, default='')
    description = models.TextField('简介', blank=True, null=True)
    img = models.CharField('鱼的图片', max_length=255, blank=True, null=True)
    fish_class = models.CharField('稀有度', max_length=50, blank=True, null=True)
    stars = models.IntegerField('收藏星级', default=0)
    rare_weight = models.CharField('上星重量', max_length=50, blank=True, null=True)
    super_rare_weight = models.CharField('蓝冠重量', max_length=50, blank=True, null=True)
    habitats = models.JSONField('栖息水域', default=list, blank=True)
    fishing_method = models.CharField('钓法', max_length=100, blank=True, default='')
    baits = models.JSONField('推荐饵料', default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

