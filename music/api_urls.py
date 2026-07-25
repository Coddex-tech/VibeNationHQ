from django.urls import path

from music.api_views import (
    SongDetailAPIView,
    DJDetailAPIView,
    MusicCommentsChunkAPIView,
    MusicRepliesChunkAPIView,
    MusicCommentCreateAPIView,
    MusicHomeAPIView,
    LatestMusicAPIView,
    GospelMusicAPIView,
    MixtapeListAPIView,
    TrendingSongAPIView,
    AlbumListAPIView,
    AlbumDetailAPIView,
    SearchAPIView,
    DownloadSongAPIView,
    SongsByTagAPIView
)

app_name = "music_api"

urlpatterns = [
    path(
        "music-home/",
        MusicHomeAPIView.as_view(),
        name="music-home-api"
    ),

    # LATEST
    path(
        "latest/",
        LatestMusicAPIView.as_view(),
        name="latest-music-api"
    ),

    # MIXTAPE
    path(
        "mixtapes/",
        MixtapeListAPIView.as_view(),
        name="mixtape-list-api"
    ),

    # GOSPEL
    path(
        "gospel/",
        GospelMusicAPIView.as_view(),
        name="gospel-music-api"
    ),

    # TRENDING SONG
    path(
        "trending/",
        TrendingSongAPIView.as_view(),
        name="trending-song-api"
    ),

    # ALBUM LIST
    path(
        "album/",
        AlbumListAPIView.as_view(),
        name="album-list-api"
    ),

    # ALBUM DETAILS
    path(
        "album-details/<slug:slug>/",
        AlbumDetailAPIView.as_view(),
        name="album-detail-api"
    ),

    # SEARCH
    path(
        "search/",
        SearchAPIView.as_view(),
        name="search-api"
    ),

    # DOWNLOAD SONG
    path(
        "download/<slug:slug>/",
        DownloadSongAPIView.as_view(),
        name="download-song-api"
    ),

    # SONG TAGS
    path(
        "tags/<slug:tag_slug>/",
        SongsByTagAPIView.as_view(),
        name="songs-by-tag-api"
    ),

    # SONG DETAIL
    path(
        "song/<slug:slug>/",
        SongDetailAPIView.as_view(),
        name="song_detail_api",
    ),

    # DJ
    path(
        "dj/<slug:slug>/",
        DJDetailAPIView.as_view(),
        name="dj_detail_api",
    ),

    # POST COMMENTS
    path(
        "<slug:slug>/comment/",
        MusicCommentCreateAPIView.as_view(),
        name="comment_create",
    ),

    # COMMENTS
    path(
        "<slug:slug>/comments/",
        MusicCommentsChunkAPIView.as_view(),
        name="comments_chunk",
    ),

    # REPLIES
    path(
        "comments/<int:comment_id>/replies/",
        MusicRepliesChunkAPIView.as_view(),
        name="replies_chunk",
    ),
]