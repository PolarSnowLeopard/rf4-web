from wiki.models import Catch
from rest_framework import serializers

class CatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catch
        fields = '__all__'

class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True, help_text="上传的鱼类图片")
    
    def validate_image(self, value):
        # 文件大小验证 (限制为10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("图片大小不能超过10MB")
        
        # 文件类型验证
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("文件必须是图片格式")
            
        return value

class FishCatchItemSerializer(serializers.Serializer):
    """单个鱼类捕获信息的序列化器"""
    time_percentage = serializers.CharField(help_text="时间和百分比，例如'42分-97%'")
    fish_name = serializers.CharField(help_text="鱼类名称，例如'镜鲤'")
    weight = serializers.CharField(help_text="重量，例如'3.705公斤'")
    score = serializers.CharField(help_text="分数，例如'2.59'")
    
    def to_internal_value(self, data):
        """将列表数据转换为字典"""
        if isinstance(data, list) and len(data) == 4:
            return {
                'time_percentage': data[0],
                'fish_name': data[1],
                'weight': data[2],
                'score': data[3]
            }
        return super().to_internal_value(data)

class ImageProcessingResponseSerializer(serializers.Serializer):
    image = serializers.CharField(help_text="处理后的图片（Base64编码）")
    fishes = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField(allow_blank=True)),
        help_text="识别出的鱼类列表，格式为二维数组 [[时间百分比, 鱼名, 重量, 分数], ...]"
    ) 