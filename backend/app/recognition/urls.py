from django.urls import path
from recognition.views.imageView import get_catch_from_image

urlpatterns = [
    path('catch_from_image', get_catch_from_image),
]
