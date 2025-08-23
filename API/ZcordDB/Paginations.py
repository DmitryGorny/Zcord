from rest_framework.pagination import LimitOffsetPagination


class LimitPagination(LimitOffsetPagination):
    default_limit = None
    max_limit = 50

    def get_limit(self, request):
        if 'limit' in request.query_params:
            return super().get_limit(request)
        return None
