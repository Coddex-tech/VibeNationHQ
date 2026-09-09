from django.urls import path

from music.api.views.catalog import (
    SongListAPIView,
    SongDetailAPIView,
    AlbumListAPIView,
    AlbumDetailAPIView,
    ArtistListAPIView,
    ArtistDetailAPIView,
    GenreListAPIView,
)

from music.api.views.community import (
    CommunityPostListCreateAPIView,
    CommunityPostDetailAPIView,
    CommunityPostCommentListCreateAPIView,
    CommunityPostCommentDetailAPIView,
    CommunityPostLikeAPIView,
    CommunityPostCommentLikeAPIView,
    CommunityPostReportAPIView,
    CommunityPostCommentReportAPIView,
)


app_name = "music_api"


urlpatterns = [
# ==================
# CATALOG
# ==================
    path(
        "songs/",
        SongListAPIView.as_view(),
        name="song-list",
    ),

    path(
        "songs/<slug:slug>/",
        SongDetailAPIView.as_view(),
        name="song-detail",
    ),

    path(
        "albums/",
        AlbumListAPIView.as_view(),
        name="album-list",
    ),

    path(
        "albums/<slug:slug>/",
        AlbumDetailAPIView.as_view(),
        name="album-detail",
    ),

    path(
        "artists/",
        ArtistListAPIView.as_view(),
        name="artist-list",
    ),
    
    path(
        "artists/<slug:slug>/",
        ArtistDetailAPIView.as_view(),
        name="artist-detail",
    ),

    path(
        "genres/",
        GenreListAPIView.as_view(),
        name="genre-list",
    ),

# =================
# COMMUNITY
# =================
    path(
        "community/posts/",
        CommunityPostListCreateAPIView.as_view(),
        name="community-post-list",
    ),

    path(
        "community/posts/<int:pk>/",
        CommunityPostDetailAPIView.as_view(),
        name="community-post-detail",
    ),

    path(
        "community/posts/<int:post_id>/comments/",
        CommunityPostCommentListCreateAPIView.as_view(),
        name="community-post-comment-list",
    ),

    path(
        "community/comments/<int:pk>/",
        CommunityPostCommentDetailAPIView.as_view(),
        name="community-comment-detail",
    ),

    path(
        "community/posts/<int:pk>/like/",
        CommunityPostLikeAPIView.as_view(),
        name="community-post-like",
    ),

    path(
        "community/comments/<int:pk>/like/",
        CommunityPostCommentLikeAPIView.as_view(),
        name="community-comment-like",
    ),

    path(
        "community/posts/<int:pk>/report/",
        CommunityPostReportAPIView.as_view(),
        name="community-post-report",
    ),

    path(
        "community/comments/<int:pk>/report/",
        CommunityPostCommentReportAPIView.as_view(),
        name="community-comment-report",
    ),

]