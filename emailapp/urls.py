from django.urls import path, include
from . import views
from .views import ChannelAssignUserView, ChannelListCreateView, ChannelListView, ChannelRemoveUserView, CreateSuperUser, CreateUser, EmailListView, LoginView, MailBoxBundleListView, MailboxBundleCreateView, PriorityChangeView, ProfileListView, SentListView, DraftsListView, EmailRepliesView, StatusChangeView, UpdateAssignedToView, UpdateChannel, UpdateMailboxBundle, UpdateProfile, UserListView
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

    path('user-list', UserListView.as_view(), name='user-list'),
    path('profile-list', ProfileListView.as_view(), name='profile-list'),
    path('user-edit', UpdateProfile.as_view(), name='user-edit'),

    path('channels', ChannelListView.as_view(), name='channels'),
    path('channels-create', ChannelListCreateView.as_view(), name='channels-create'),
    path('channels-edit', UpdateChannel.as_view(), name='channels-edit'),
    path('assign-channels', ChannelAssignUserView.as_view(), name='assign-channels'),
    path('assign-remove', ChannelRemoveUserView.as_view(), name='assign-remove'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('mailbox', MailBoxBundleListView.as_view(), name='mailbox'),
    path('mailbox-create', MailboxBundleCreateView.as_view(), name='mailbox-create'),
    path('mailbox-edit', UpdateMailboxBundle.as_view(), name='mailbox-edit'),

    path('assignedTo-edit', UpdateAssignedToView.as_view(), name='assignedTo-edit'),
    path('priority-edit', PriorityChangeView.as_view(), name='priority-edit'),
    path('status-edit', StatusChangeView.as_view(), name='status-edit'),
]