from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from wiki.models import Accessory
from wiki.serializers.accessorySerializer import AccessorySerializer


class AccessoryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def accessory_list(request):
    queryset = Accessory.objects.all().order_by('id')
    accessory_type = request.query_params.get('accessory_type')
    search = request.query_params.get('search')
    if accessory_type:
        queryset = queryset.filter(accessory_type=accessory_type)
    if search:
        queryset = queryset.filter(name__icontains=search)
    paginator = AccessoryPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = AccessorySerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def accessory_detail(request, pk):
    try:
        acc = Accessory.objects.get(pk=pk)
    except Accessory.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    serializer = AccessorySerializer(acc)
    return Response(serializer.data)


@api_view(['GET'])
def accessory_types(request):
    types = Accessory.objects.values_list('accessory_type', flat=True).distinct().order_by('accessory_type')
    return Response(list(types))
