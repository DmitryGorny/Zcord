from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class LimitPagination(LimitOffsetPagination):
    default_limit = None
    max_limit = 50

    def get_limit(self, request):
        if 'limit' in request.query_params:
            return super().get_limit(request)
        return None

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': list(data)
        })
