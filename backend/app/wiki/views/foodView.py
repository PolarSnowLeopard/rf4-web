from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from wiki.models import Food
from wiki.serializers.foodSerializer import FoodSerializer


class FoodPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def food_list(request):
    queryset = Food.objects.all().order_by('id')
    food_type = request.query_params.get('food_type')
    search = request.query_params.get('search')
    if food_type:
        queryset = queryset.filter(food_type=food_type)
    if search:
        queryset = queryset.filter(name__icontains=search)
    paginator = FoodPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = FoodSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def food_detail(request, pk):
    try:
        food = Food.objects.get(pk=pk)
    except Food.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
    serializer = FoodSerializer(food)
    return Response(serializer.data)


@api_view(['GET'])
def food_types(request):
    types = Food.objects.values_list('food_type', flat=True).distinct().order_by('food_type')
    return Response(list(types))
