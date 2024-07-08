from django.urls import path, include
from . import views
from .views import ChannelAssignUserView, ChannelListCreateView, ChannelListView, CreateSuperUser, CreateUser, EmailListView, LoginView, ProfileListView, SentListView, DraftsListView, EmailRepliesView, UserListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # path('', views.email_list, name='email_list'),
    path('inbox', EmailListView.as_view(), name='inbox'),
    path('sent', SentListView.as_view(), name='sent'),
    path('drafts', DraftsListView.as_view(), name='drafts'),
    path('replies', EmailRepliesView.as_view(), name='email_replies'),
    # path('email_list/', views.email_list, name='email_list'),

    path('login', LoginView.as_view(), name='login'),
    path('create-superuser', CreateSuperUser.as_view(), name='create-superuser'),
    path('create-user', CreateUser.as_view(), name='create-user'),

    path('channels', ChannelListView.as_view(), name='channels'),
    path('channels-create', ChannelListCreateView.as_view(), name='channels-create'),

    path('user-list', UserListView.as_view(), name='user-list'),
    path('profile-list', ProfileListView.as_view(), name='profile-list'),

    path('assign-channels', ChannelAssignUserView.as_view(), name='assign-channels'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]