from django.urls import path
from . import views
app_name = 'account'
urlpatterns = [
	path('', views.login_view, name = 'login'),
	path('home/', views.home, name = 'home'),
	path('logout/', views.logout_view, name = 'logout'),
	path('register/', views.register_view, name = 'register'),
	path('account/<username>/', views.account_view, name = 'view'),
	path('account/<str:username>/<str:room_name>', views.room, name= 'room'),
	path('account/<username>/edit/', views.edit_view, name = 'edit-view'),
	path('account/<str:writer>/post/<int:pk>/', views.post_view, name='post-view'),
	path('account/<str:writer>/post/<int:pk>/delete/', views.post_delete, name='post-delete'),
	path('<str:writer>/new-post/', views.new_post_view, name = 'new-post'),
	path('search/', views.search_view, name = 'search'),
	path('followToggle/<str:author>/', views.followToggle, name = 'followToggle'),
	path('update_likes/', views.updateLikes, name='updating-likes'),
	path('comment_send/', views.commentSend, name='comment-sendingg')
]