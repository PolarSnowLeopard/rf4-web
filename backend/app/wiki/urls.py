from django.urls import path
from wiki.views.fishView import fish_list, fish_detail
from wiki.views.baitView import bait_list, bait_detail, bait_types

urlpatterns = [
    path('fish', fish_list),
    path('fish/<str:name>', fish_detail),
    path('bait', bait_list),
    path('bait/types', bait_types),
    path('bait/<int:pk>', bait_detail),
]