from django.urls import path
from . import views
from .views import route_list, login_view
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', login_view , name='login'),

    path('routes/', route_list, name='route_list'),
    path('upload-image/', upload_image, name='upload_image'),


    path('ranking/',views.RankingView.as_view(),name='ranking'),
    path('chat/',views.ChatView.as_view(),name='chat'),

    path('prayers/',prayers_list,name='prayers_list'),
    path('create_prayers_post/', create_prayers_post, name='create_prayers_post'),
    path('prayers/edit/<int:post_id>/', edit_prayers, name='edit_prayers'),
    path('prayers/delete/<int:post_id>/', delete_prayers, name='delete_prayers'),

    path('news/', news_list, name='news_list'),
    path('create_news_post/', create_news_post, name='create_news_post'),
    path('news/edit/<int:post_id>/', edit_news, name='edit_news'),
    path('news/delete/<int:post_id>/', delete_news, name='delete_news'),

    path('user/', UserView ,name='user'),
    path('dashboard/',dashboard,name='dashboard'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),

    path('setting/',edit_profile,name='setting'),
    path('logout/',logout_view,name='logout')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
