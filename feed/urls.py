from django.urls import path
#Password Reset Import#
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    #HomePage
    path('', views.home, name="home"),

    #Add Comment
    path('post/add-comment/<int:post_id>', views.add_comment, name="add_comment"),


    #Increment or Decrement Likes on Posts
    path('like-counter/', views.like_count, name="like-count"),

    #Login Users
    path('login/', views.login_page, name='login'),

    #Logout Users
    path('logout/', views.logout_page, name='logout'),

    #User Validation and Registration
    path('register/', views.register_page, name='register'),

    #Redirect to Profile Page
    path('profile/<pk>/', views.profile_page, name='profile'),

    #Retrieve Notifications
    path('notification/', views.notification, name='notification'),

    #Create Posts
    path('create-post/', views.create_post, name='create_post'),

    #Edit Posts
    path('edit-post/<int:postid>/', views.edit_post, name='edit_post'),

    #Create Notifications
    path('delete-post/<int:postid>/', views.delete_post, name='delete_post'),

    #Delete Notifications
    path('remove-notification/<int:id>/', views.remove_notification, name='remove_notification'),

    #Notification Mark as Read
    path('mark-as-read/<int:id>/', views.mark_as_read, name="mark_as_read"),

    #Delete Read Notifications
    path('clear-unread-notifications/', views.clear_all_unread_notifications, name="clear_all_unread_notifications"),

    #Delete Unread Notifications
    path('clear-read-notifications/', views.clear_all_read_notifications, name="clear_all_read_notifications"),

    #Follow Users
    path('follow-user/<int:userid>/', views.follow_user, name="follow_user"),
    
    # Search User
    path('search-user/<str:user>/', views.search_user, name="search_user"),

    #Comment
    path('post/comment/<str:post_id>/', views.comment, name='comment'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name = 'password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name= 'password_reset_done.html'), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name="password_reset_confirm"),
    path('reset/done/', auth_views.PasswordChangeDoneView.as_view(template_name = 'password_reset_complete.html'), name="password_reset_complete")
]