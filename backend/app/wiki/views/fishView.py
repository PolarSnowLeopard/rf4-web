from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from wiki.models import Fish
from wiki.serializers.fishSerializer import FishSerializer

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def fish_list(request):
    if request.method == 'GET':
        search_query = request.query_params.get('search', None)
        fish_class = request.query_params.get('fish_class', None)

        queryset = Fish.objects.all()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        if fish_class:
            queryset = queryset.filter(fish_class=fish_class)

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = FishSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        if not request.user or not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = FishSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def fish_detail(request, name: str):
    try:
        fish = Fish.objects.get(name=name)
    except Fish.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FishSerializer(fish)
        return Response(serializer.data)

    if not request.user or not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PUT':
        serializer = FishSerializer(fish, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        fish.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
