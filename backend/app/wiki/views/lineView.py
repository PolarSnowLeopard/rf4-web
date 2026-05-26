from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from wiki.models import Line
from wiki.serializers.lineSerializer import LineSerializer


class LinePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def line_list(request):
    queryset = Line.objects.all().order_by('id')
    search = request.query_params.get('search', '')
    if search:
        queryset = queryset.filter(name__icontains=search)
    line_type = request.query_params.get('line_type', '')
    if line_type:
        queryset = queryset.filter(line_type=line_type)
    paginator = LinePagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = LineSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def line_detail(request, pk):
    try:
        line = Line.objects.get(pk=pk)
    except Line.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    serializer = LineSerializer(line)
    return Response(serializer.data)


@api_view(['GET'])
def line_types(request):
    types = Line.objects.values_list('line_type', flat=True).distinct().order_by('line_type')
    return Response(list(types))
