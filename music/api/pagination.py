from rest_framework.pagination import PageNumberPagination


class MusicPagination(PageNumberPagination):
    """
    Pagination for VibeNation music catalog endpoints.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class CommunityCommentThreadPagination(PageNumberPagination):
    """
    Pagination for all replies belonging to one root comment.

    Each request returns at most five replies.
    The response count represents all published descendants
    in the conversation, not only direct replies.
    """

    page_size = 5
    page_size_query_param = None