from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from wiki.models import Fish
from wiki.serializers.fishSerializer import FishSerializer

from rest_framework.pagination import PageNumberPagination

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
