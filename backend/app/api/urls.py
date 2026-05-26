from django.urls import path, include

urlpatterns = [
    path('user/', include('user.urls')),
    path('wiki/', include('wiki.urls')),
    path('recognition/', include('recognition.urls')),
    path('agent/', include('agent.urls')),
]