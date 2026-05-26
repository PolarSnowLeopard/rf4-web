from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from wiki.models import Lure
from wiki.serializers.lureSerializer import LureSerializer
from rest_framework.pagination import PageNumberPagination


class LurePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([AllowAny])
def lure_list(request):
    search_query = request.query_params.get('search', None)
    lure_type = request.query_params.get('lure_type', None)

    queryset = Lure.objects.all()

    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    if lure_type:
        queryset = queryset.filter(lure_type=lure_type)

    paginator = LurePagination()
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = LureSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def lure_types(request):
    types = Lure.objects.values_list('lure_type', flat=True).distinct().order_by('lure_type')
    return Response([t for t in types if t])


@api_view(['GET'])
@permission_classes([AllowAny])
def lure_detail(request, pk: int):
    try:
        lure = Lure.objects.get(pk=pk)
    except Lure.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = LureSerializer(lure)
    return Response(serializer.data)
