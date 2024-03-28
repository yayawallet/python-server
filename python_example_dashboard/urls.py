from django.urls import include, path

urlpatterns = [
    path('example/', include('example.urls')),
]
