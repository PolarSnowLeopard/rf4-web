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


class Bait(models.Model):
    """鱼饵"""
    name = models.CharField('名称', max_length=200)
    description = models.TextField('描述', blank=True, default='')
    img = models.CharField('图片', max_length=255, blank=True, default='')
    bait_type = models.CharField('形式', max_length=100, blank=True, default='')
    buoyancy = models.CharField('浮力', max_length=50, blank=True, default='')
    weight = models.CharField('质量', max_length=50, blank=True, default='')
    water_weight = models.CharField('水中重量', max_length=50, blank=True, default='')
    hook_size = models.CharField('鱼钩尺寸', max_length=100, blank=True, default='')
    brand = models.CharField('品牌', max_length=100, blank=True, default='')
    size = models.CharField('大小', max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'bait_type'], name='unique_bait_name_type')
        ]

    def __str__(self):
        return self.name


class Lure(models.Model):
    """拟饵"""
    name = models.CharField('名称', max_length=200)
    description = models.TextField('描述', blank=True, default='')
    img = models.CharField('图片', max_length=255, blank=True, default='')
    lure_type = models.CharField('形式', max_length=100, blank=True, default='')
    length = models.CharField('长度', max_length=50, blank=True, default='')
    size = models.CharField('大小', max_length=50, blank=True, default='')
    weight = models.CharField('质量', max_length=50, blank=True, default='')
    hook_size = models.CharField('鱼钩尺寸', max_length=100, blank=True, default='')
    unlock_skill = models.CharField('解锁技能', max_length=200, blank=True, default='')
    hook_component = models.CharField('钓钩组件', max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'lure_type'], name='unique_lure_name_type')
        ]

    def __str__(self):
        return self.name


class Rod(models.Model):
    """渔竿"""
    name = models.CharField('名称', max_length=200)
    description = models.TextField('描述', blank=True, default='')
    img = models.CharField('图片', max_length=255, blank=True, default='')
    rod_type = models.CharField('类型', max_length=100, blank=True, default='')
    sensitivity = models.CharField('灵敏度', max_length=50, blank=True, default='')
    structure = models.CharField('结构', max_length=100, blank=True, default='')
    hardness = models.CharField('硬度', max_length=50, blank=True, default='')
    capacity = models.CharField('能力', max_length=50, blank=True, default='')
    length = models.CharField('长度', max_length=50, blank=True, default='')
    strength = models.CharField('强度', max_length=50, blank=True, default='')
    level_req = models.CharField('等级要求', max_length=50, blank=True, default='')
    cast_weight = models.CharField('适配重', max_length=50, blank=True, default='')
    weight = models.CharField('质量', max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'rod_type'], name='unique_rod_name_type')
        ]

    def __str__(self):
        return self.name

