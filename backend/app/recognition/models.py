from django.db import models


class Catch(models.Model):
    """鱼获"""
    species = models.CharField('种类', max_length=100, blank=True, null=True)
    weight = models.CharField('重量', max_length=50, blank=True, null=True)
    price = models.IntegerField('价格', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
