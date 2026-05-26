from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from wiki.models import Groundbait
from wiki.serializers.groundbaitSerializer import GroundbaitSerializer


class GroundbaitPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def groundbait_list(request):
    queryset = Groundbait.objects.all().order_by('id')
    groundbait_type = request.query_params.get('groundbait_type')
    search = request.query_params.get('search')
    if groundbait_type:
        queryset = queryset.filter(groundbait_type=groundbait_type)
    if search:
        queryset = queryset.filter(name__icontains=search)
    paginator = GroundbaitPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = GroundbaitSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def groundbait_detail(request, pk):
    try:
        gb = Groundbait.objects.get(pk=pk)
    except Groundbait.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    serializer = GroundbaitSerializer(gb)
    return Response(serializer.data)


@api_view(['GET'])
def groundbait_types(request):
    types = Groundbait.objects.values_list('groundbait_type', flat=True).distinct().order_by('groundbait_type')
    return Response(list(types))
