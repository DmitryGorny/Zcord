from django.urls import path
from .views import UserView, FriendshipView, FriendsAddingView, MessageView

urlpatterns = [
    path('users/', UserView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='users'),
    path('users/<int:pk>/', UserView.as_view({
        'get': 'retrieve',
        'delete': 'destroy',
        'put': 'update',
        'patch': 'partial_update'
    }), name='users-detail'),

    path('friendship/', FriendshipView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='friendship'),
    path('friendship/<int:pk>/', FriendshipView.as_view({
        'get': 'retrieve',
        'delete': 'destroy',
        'put': 'update',
        'patch': 'partial_update'
    }), name='friendship-detail'),

    path('friends_adding/', FriendsAddingView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='friends_adding'),
    path('friends_adding/<int:pk>/', FriendsAddingView.as_view({
        'get': 'retrieve',
        'delete': 'destroy',
        'put': 'update',
        'patch': 'partial_update'
    }), name='friends_adding-detail'),

    path('messages/', MessageView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='messages'),
    path('messages/<int:pk>/', MessageView.as_view({
        'get': 'retrieve',
        'delete': 'destroy',
        'put': 'update',
        'patch': 'partial_update'
    }), name='messages-detail'),
    path('messages-bulk/', MessageView.as_view({
        'get': 'list',
        'post': 'bulk_create'
    }), name='message_bulk_create'),
    path('messages-bulk-update/', MessageView.as_view({
        'get': 'list',
        'post': 'bulk_update'
    }), name='message_bulk_update'),
    path('messages-unseen-count/', MessageView.as_view({
        'get': 'get_unseen_count',
    }), name='messages-unseen-count')
]
