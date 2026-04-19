from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from wiki.models import Fish, Catch
from wiki.serializers.fishSerializer import FishSerializer
from wiki.serializers.catchSerializer import CatchSerializer, ImageUploadSerializer, ImageProcessingResponseSerializer

from services.catch_extractor.main import extract_fishes
from rest_framework.pagination import PageNumberPagination

import os
from django.conf import settings
import base64
from io import BytesIO
from django.db.models import Q

class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def fish_list(request):
    if request.method == 'GET':
        # 获取查询参数
        search_query = request.query_params.get('search', None)
        fish_class = request.query_params.get('fish_class', None)
        
        # 初始查询集
        queryset = Fish.objects.all()
        
        # 应用搜索过滤
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        # 应用类别过滤
        if fish_class:
            queryset = queryset.filter(fish_class=fish_class)
        
        # 分页
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        
        # 序列化
        serializer = FishSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
        serializer = FishSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def fish_detail(request, name: str):
    try:
        fish = Fish.objects.get(name=name)
    except Fish.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = FishSerializer(fish)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = FishSerializer(fish, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        fish.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
    
    # 保存图片
    image_path = os.path.join(settings.ASSETS_DIR, 'original_image.png')
    if not os.path.exists(os.path.dirname(image_path)):
        os.makedirs(os.path.dirname(image_path))

    with open(image_path, 'wb') as f:
        f.write(original_image.read())
    
    # 调用extract_fishes
    image, fishes = extract_fishes(image_path=image_path)

    # 保存处理后的图片
    with open(os.path.join(settings.ASSETS_DIR, 'result_image.png'), 'wb') as f:
        image.save(f, format='PNG')

    # base64编码
    img_buffer = BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    image = base64.b64encode(img_buffer.read()).decode('utf-8')

    # 准备响应数据
    response_data = {
        'image': image,
        'fishes': fishes
    }
    
    # 使用响应序列化器验证响应格式
    response_serializer = ImageProcessingResponseSerializer(data=response_data)
    response_serializer.is_valid(raise_exception=True)
    
    # 返回验证后的数据
    return Response(response_serializer.validated_data)