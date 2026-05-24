from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from recognition.serializers.catchSerializer import ImageUploadSerializer, ImageProcessingResponseSerializer
from services.catch_extractor.main import extract_fishes

import os
from django.conf import settings
import base64
from io import BytesIO


@api_view(['POST'])
@permission_classes([AllowAny])
def get_catch_from_image(request):
    """
    从上传的图片中识别渔获信息
    ---
    请求体:
      image: 鱼类图片文件
    响应:
      image: 处理后的图片（Base64编码）
      fishes: 识别出的渔获列表，格式为二维数组:
        [[时间百分比, 鱼名, 重量, 分数],
         [时间百分比, 鱼名, 重量, 分数], ...]

        例如: [["42分-97%", "镜鲤", "3.705公斤", "2.59"], ...]
    """
    serializer = ImageUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    original_image = serializer.validated_data['image']

    image_path = os.path.join(settings.ASSETS_DIR, 'original_image.png')
    if not os.path.exists(os.path.dirname(image_path)):
        os.makedirs(os.path.dirname(image_path))

    with open(image_path, 'wb') as f:
        f.write(original_image.read())

    image, fishes = extract_fishes(image_path=image_path)

    with open(os.path.join(settings.ASSETS_DIR, 'result_image.png'), 'wb') as f:
        image.save(f, format='PNG')

    img_buffer = BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    image = base64.b64encode(img_buffer.read()).decode('utf-8')

    response_data = {
        'image': image,
        'fishes': fishes
    }

    response_serializer = ImageProcessingResponseSerializer(data=response_data)
    response_serializer.is_valid(raise_exception=True)

    return Response(response_serializer.validated_data)
