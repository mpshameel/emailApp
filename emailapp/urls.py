from django.urls import path, include
from . import views
from .views import EmailListView, SentListView, DraftsListView, EmailRepliesView



urlpatterns = [
    # path('', views.email_list, name='email_list'),
    path('inbox', EmailListView.as_view(), name='inbox'),
    path('sent', SentListView.as_view(), name='sent'),
    path('drafts', DraftsListView.as_view(), name='drafts'),
    path('replies', EmailRepliesView.as_view(), name='email_replies'),
    # path('email_list/', views.email_list, name='email_list'),
]