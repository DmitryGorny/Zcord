from django.urls import path
from .views import UserView, FriendshipView, FriendsAddingView, MessageView, ChatsView, GroupsRequestView, \
    GroupsMembers, GroupsMembersView, GroupsView

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
        'post': 'create',
        'delete': 'destroy'
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
    }), name='messages-unseen-count'),

    path('chats/', ChatsView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='chats'),
    path('chats/<int:pk>/', ChatsView.as_view({
        'get': 'retrieve'
    }), name='chats-pk'),
    path('chats/delete/<str:DM_id>/', ChatsView.as_view({
        'delete': 'destroy'
    }), name='chats-dm-destroy'),
    path('chats/delete/<str:group_id>/', ChatsView.as_view({
        'delete': 'destroy'
    }), name='chats-dm-destroy'),
    path('chats/delete/groups/<str:groups_id>/', ChatsView.as_view({
        'delete': 'destroy'
    }), name='chats-group-destroy'),

    path('groups-members/', GroupsMembersView.as_view({
        'get': 'list',
        'post': 'create',
    }), name='groups-members'),
    path('groups-members/<int:pk>/', GroupsMembersView.as_view({
        'get': 'retrieve',
        'delete': 'destroy',
        'patch': 'update'
    }), name='groups-members-by-group-id'),

    path('groups-requests/', GroupsRequestView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='groups-requests'),
    path('groups-requests/<int:pk>/', GroupsRequestView.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='groups-requests-pk'),

    path('groups/', GroupsView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='groups'),
    path('groups/<int:pk>/', GroupsView.as_view({
        'get': 'retrieve',
        'patch': 'partial_update'
    }), name='groups-detail'),
    path('groups/groups-name-unique/', GroupsView.as_view({
        'get': 'check_name',
    }), name='groups-name-unique')
]
