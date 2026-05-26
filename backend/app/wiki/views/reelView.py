from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from wiki.models import Reel
from wiki.serializers.reelSerializer import ReelSerializer


class ReelPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def reel_list(request):
    queryset = Reel.objects.all().order_by('id')
    search = request.query_params.get('search', '')
    if search:
        queryset = queryset.filter(name__icontains=search)
    reel_type = request.query_params.get('reel_type', '')
    if reel_type:
        queryset = queryset.filter(reel_type=reel_type)
    paginator = ReelPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = ReelSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def reel_detail(request, pk):
    try:
        reel = Reel.objects.get(pk=pk)
    except Reel.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    serializer = ReelSerializer(reel)
    return Response(serializer.data)


@api_view(['GET'])
def reel_types(request):
    types = Reel.objects.values_list('reel_type', flat=True).distinct().order_by('reel_type')
    return Response(list(types))
