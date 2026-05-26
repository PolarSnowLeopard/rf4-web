from django.urls import path
from wiki.views.fishView import fish_list, fish_detail
from wiki.views.baitView import bait_list, bait_detail, bait_types
from wiki.views.lureView import lure_list, lure_detail, lure_types
from wiki.views.rodView import rod_list, rod_detail, rod_types
from wiki.views.reelView import reel_list, reel_detail, reel_types
from wiki.views.lineView import line_list, line_detail, line_types
from wiki.views.hookView import hook_list, hook_detail, hook_types
from wiki.views.rigView import rig_list, rig_detail, rig_types
from wiki.views.groundbaitView import groundbait_list, groundbait_detail, groundbait_types

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
    path('line', line_list),
    path('line/types', line_types),
    path('line/<int:pk>', line_detail),
    path('hook', hook_list),
    path('hook/types', hook_types),
    path('hook/<int:pk>', hook_detail),
    path('rig', rig_list),
    path('rig/types', rig_types),
    path('rig/<int:pk>', rig_detail),
    path('groundbait', groundbait_list),
    path('groundbait/types', groundbait_types),
    path('groundbait/<int:pk>', groundbait_detail),
]