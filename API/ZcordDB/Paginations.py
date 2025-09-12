from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class LimitPagination(LimitOffsetPagination):
    default_limit = None
    max_limit = 50

    def get_limit(self, request):
        if 'limit' in request.query_params:
            return super().get_limit(request)
        return None

    def get_offset(self, request):
        if "offset" in request.query_params:
            return super().get_offset(request)
        return None

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.count = self.get_count(queryset)
        self.request = request

        if self.limit is None:
            self.limit = 0

        if self.offset is None:
            self.offset = 0

        if self.offset == 0 and self.limit == 0:
            return list(queryset)

        if self.count == 0 or self.offset > self.count:
            return []

        return list(queryset[self.offset:self.offset + self.limit])

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'limit': self.limit,
            'offset': self.offset,
            'results': list(reversed(data))
        })
