from django.urls import path , include
from . import views

urlpatterns = [
    path('routes/', views.get_routes, name='route_list'),
    path("__reload__/", include("django_browser_reload.urls")),
]
