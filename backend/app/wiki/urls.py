from django.urls import path
from wiki.views.fishView import fish_list, fish_detail, get_catch_from_image

urlpatterns = [
    path('fish', fish_list),
    path('fish/<str:name>', fish_detail),
    path('catch_from_image', get_catch_from_image),
]