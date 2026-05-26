from django.urls import path
from wiki.views.fishView import fish_list, fish_detail
from wiki.views.baitView import bait_list, bait_detail, bait_types
from wiki.views.lureView import lure_list, lure_detail, lure_types
from wiki.views.rodView import rod_list, rod_detail, rod_types
from wiki.views.reelView import reel_list, reel_detail, reel_types

urlpatterns = [
    path('fish', fish_list),
    path('fish/<str:name>', fish_detail),
    path('bait', bait_list),
    path('bait/types', bait_types),
    path('bait/<int:pk>', bait_detail),
    path('lure', lure_list),
    path('lure/types', lure_types),
    path('lure/<int:pk>', lure_detail),
    path('rod', rod_list),
    path('rod/types', rod_types),
    path('rod/<int:pk>', rod_detail),
    path('reel', reel_list),
    path('reel/types', reel_types),
    path('reel/<int:pk>', reel_detail),
]