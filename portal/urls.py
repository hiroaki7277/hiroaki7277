from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'portal'

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat_room, name='chat_room'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('comment/<int:post_id>/<int:parent_id>/', views.add_reply, name='add_reply'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('<str:item_type>/<int:item_id>/like/', views.like_item, name='like_item'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', auth_views.LoginView.as_view(template_name='portal/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='portal:home'), name='logout'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='portal/password_change.html'),
        name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='portal/password_change_done.html'),
        name='password_change_done'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='portal/password_reset.html',
        email_template_name='portal/password_reset_email.html',
        subject_template_name='portal/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='portal/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='portal/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='portal/password_reset_complete.html'
    ), name='password_reset_complete'),
]