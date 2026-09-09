from django.urls import path

# from music.api_views import (
#     MusicCommentsChunkAPIView,
#     MusicRepliesChunkAPIView,
#     MusicCommentCreateAPIView,
# )

app_name = "music_api"

urlpatterns = [

    # # POST COMMENTS
    # path(
    #     "<slug:slug>/comment/",
    #     MusicCommentCreateAPIView.as_view(),
    #     name="comment_create",
    # ),

    # # COMMENTS
    # path(
    #     "<slug:slug>/comments/",
    #     MusicCommentsChunkAPIView.as_view(),
    #     name="comments_chunk",
    # ),

    # # REPLIES
    # path(
    #     "comments/<int:comment_id>/replies/",
    #     MusicRepliesChunkAPIView.as_view(),
    #     name="replies_chunk",
    # ),
]