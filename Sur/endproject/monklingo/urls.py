from django.urls import path
from . import views
from .views import route_list, login_view
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', login_view , name='login'),
    

    path('routes/', route_list, name='route_list'),
    path('api/routes/', list_routes, name='list_routes'),
    path('api/routes/add/', add_route, name='add_route'),
    path('manage/routes/', manage_routes , name='manage_routes'),
    path('api/routes/<int:route_id>/update/', update_route, name='update_route'),
    path('api/routes/<int:route_id>/delete/', delete_route, name='delete_route'),
    path('check-daily-photo/', check_daily_photo, name='check_daily_photo'),
    path('capture/', capture_view, name='capture'),

    path('api/routes/<int:route_id>/checkpoints/', list_checkpoints, name='list_checkpoints'),
    path('api/routes/<int:route_id>/checkpoints/add/', add_checkpoint, name='add_checkpoint'),
    path('api/checkpoints/<int:checkpoint_id>/delete/', delete_checkpoint, name='delete_checkpoint'),
    path('api/checkpoints/<int:checkpoint_id>/update/', update_checkpoint, name='update_checkpoint'),

    path('api/routes/<int:temple_id>/', get_routes_by_temple, name='routes_by_temple'),
    path("api/temples/", temple_list, name="temple-list"),
    path("api/temples/add/", add_temple, name="add-temple"),
    path("api/temples/<int:temple_id>/delete/", delete_temple, name="delete_temple"),
    path('upload-image/', upload_image, name='upload_image'),


    path('ranking/',ranking_view,name='ranking'),

    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/<int:room_id>/messages/', views.chat_room_messages, name='chat_room_messages'),
    path('chat/add/', views.chat_room_create, name='chat_room_create'),
    path('chat/<int:room_id>/edit/', views.chat_room_update, name='chat_room_update'),
    path('chat/<int:room_id>/delete/', views.chat_room_delete, name='chat_room_delete'),

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
    path('logout/',logout_view,name='logout'),
    path("robots.txt", robots_txt),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
