from django.db import models

# Create your models here.
class Fish(models.Model):
    """鱼类"""
    name = models.CharField('名称（种类）', unique=True, max_length=100, blank=True, null=True)
    description = models.TextField('简介', blank=True, null=True)
    img = models.CharField('鱼的图片', max_length=255, blank=True, null=True)
    fish_class = models.CharField('稀有度', max_length=50, blank=True, null=True)
    rare_weight = models.CharField('上星重量', max_length=50, blank=True, null=True)
    super_rare_weight = models.CharField('蓝冠重量', max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Catch(models.Model):
    """鱼获"""
    # fish = models.ForeignKey(Fish, on_delete=models.CASCADE)
    species = models.CharField('种类', max_length=100, blank=True, null=True)
    weight = models.CharField('重量', max_length=50, blank=True, null=True)
    price = models.IntegerField('价格', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
