from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from wiki.models import Rig
from wiki.serializers.rigSerializer import RigSerializer


class RigPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def rig_list(request):
    queryset = Rig.objects.all().order_by('id')
    rig_type = request.query_params.get('rig_type')
    search = request.query_params.get('search')
    if rig_type:
        queryset = queryset.filter(rig_type=rig_type)
    if search:
        queryset = queryset.filter(name__icontains=search)
    paginator = RigPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = RigSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def rig_detail(request, pk):
    try:
        rig = Rig.objects.get(pk=pk)
    except Rig.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    serializer = RigSerializer(rig)
    return Response(serializer.data)


@api_view(['GET'])
def rig_types(request):
    types = Rig.objects.values_list('rig_type', flat=True).distinct().order_by('rig_type')
    return Response(list(types))
