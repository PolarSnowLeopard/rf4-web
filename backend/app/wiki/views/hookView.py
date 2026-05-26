from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from wiki.models import Hook
from wiki.serializers.hookSerializer import HookSerializer


class HookPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def hook_list(request):
    queryset = Hook.objects.all().order_by('id')
    hook_type = request.query_params.get('hook_type')
    search = request.query_params.get('search')
    if hook_type:
        queryset = queryset.filter(hook_type=hook_type)
    if search:
        queryset = queryset.filter(name__icontains=search)
    paginator = HookPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = HookSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def hook_detail(request, pk):
    try:
        hook = Hook.objects.get(pk=pk)
    except Hook.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    serializer = HookSerializer(hook)
    return Response(serializer.data)


@api_view(['GET'])
def hook_types(request):
    types = Hook.objects.values_list('hook_type', flat=True).distinct().order_by('hook_type')
    return Response(list(types))
