from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from wiki.models import Rod
from wiki.serializers.rodSerializer import RodSerializer
from rest_framework.pagination import PageNumberPagination


class RodPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([AllowAny])
def rod_list(request):
    search_query = request.query_params.get('search', None)
    rod_type = request.query_params.get('rod_type', None)

    queryset = Rod.objects.all()

    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    if rod_type:
        queryset = queryset.filter(rod_type=rod_type)

    paginator = RodPagination()
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = RodSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def rod_types(request):
    types = Rod.objects.values_list('rod_type', flat=True).distinct().order_by('rod_type')
    return Response([t for t in types if t])


@api_view(['GET'])
@permission_classes([AllowAny])
def rod_detail(request, pk: int):
    try:
        rod = Rod.objects.get(pk=pk)
    except Rod.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = RodSerializer(rod)
    return Response(serializer.data)
