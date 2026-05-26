from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from wiki.models import Bait
from wiki.serializers.baitSerializer import BaitSerializer
from rest_framework.pagination import PageNumberPagination


class BaitPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([AllowAny])
def bait_list(request):
    search_query = request.query_params.get('search', None)
    bait_type = request.query_params.get('bait_type', None)

    queryset = Bait.objects.all()

    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    if bait_type:
        queryset = queryset.filter(bait_type=bait_type)

    paginator = BaitPagination()
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = BaitSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def bait_types(request):
    types = Bait.objects.values_list('bait_type', flat=True).distinct().order_by('bait_type')
    return Response([t for t in types if t])


@api_view(['GET'])
@permission_classes([AllowAny])
def bait_detail(request, pk: int):
    try:
        bait = Bait.objects.get(pk=pk)
    except Bait.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = BaitSerializer(bait)
    return Response(serializer.data)
