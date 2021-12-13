from rest_framework.pagination import PageNumberPagination


class AccountPageNumberPagination(PageNumberPagination):
    page_size = 10


# 페이지 네이션
class BasicPagination(PageNumberPagination):
    page_size = 18
    page_size_query_param = 'limit'


class BasicReplyPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 10