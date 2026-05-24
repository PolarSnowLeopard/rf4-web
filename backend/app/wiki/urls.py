from django.urls import path
from wiki.views.fishView import fish_list, fish_detail

urlpatterns = [
    path('fish', fish_list),
    path('fish/<str:name>', fish_detail),
]