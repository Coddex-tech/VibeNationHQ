from django.urls import path

from music.api.views.search import MusicSearchAPIView

# EXTERNAL PROVIDER
from music.api.views.provider_search import MusicProviderSearchView

from music.api.views.provider_import import MusicProviderImportView

from music.api.views.catalog_search import MusicCatalogSearchView

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
    CommunityPostViewAPIView,
    CommunityPostDetailAPIView,
    CommunityPostCommentListCreateAPIView,
    CommunityPostCommentDetailAPIView,
    CommunityPostReportAPIView,
    CommunityPostCommentReportAPIView,
    CommunityPostFavoriteAPIView,
    CommunityPostFavoriteListAPIView,
)

from music.api.views.ratings import (
    SongRatingAPIView,
    AlbumRatingAPIView,
)

from music.api.views.favorites import (
    SongFavoriteAPIView,
    AlbumFavoriteAPIView,
)

from music.api.views.follows import (
    ArtistFollowAPIView,
    UserFollowAPIView,
)

from music.api.views.likes import (
    EditorialArticleLikeAPIView,
    CommunityPostLikeAPIView,
    EditorialCommentLikeAPIView,
    CommunityPostCommentLikeAPIView,
)

from music.api.views.discovery import (
    TrendingSongsAPIView,
    TrendingAlbumsAPIView,
    TrendingArtistsAPIView,
    MostDiscussedSongsAPIView,
    MostDiscussedAlbumsAPIView,
    MostFavoritedSongsAPIView,
    MostFavoritedAlbumsAPIView,
    TopRatedSongsAPIView,
    TopRatedAlbumsAPIView,
    FeaturedSongsAPIView,
    FeaturedAlbumsAPIView,
    FeaturedArtistsAPIView,
    RecentlyReleasedSongsAPIView,
    RecentlyReleasedAlbumsAPIView,
    MusicDiscoveryAPIView,
)

from music.api.views.editorial import (
    EditorialArticleListAPIView,
    EditorialArticleDetailAPIView,
    EditorialCommentListCreateAPIView,
    EditorialCommentDetailAPIView,
    EditorialArticleReportAPIView,
    EditorialCommentReportAPIView,
)

from music.api.views.feed_interactions import (
    MusicFeedInteractionAPIView,
)

from music.api.views.genre_preferences import (
    UserGenrePreferenceListCreateAPIView,
    UserGenrePreferenceDeleteAPIView,
    UserGenrePreferenceSetAPIView,
)

from music.api.views.feed import (
    MusicFeedAPIView,
)


app_name = "music_api"


urlpatterns = [

    # ============================================================
    # SEARCH
    # ============================================================

    path(
        "search/",
        MusicSearchAPIView.as_view(),
        name="music-search",
    ),

    path(
        "search/providers/",
        MusicProviderSearchView.as_view(),
        name="provider-search",
    ),

    # ============================================================
    # EXTERNAL SEARCH CATALOG
    # ============================================================

    path(
        "catalog/search/",
        MusicCatalogSearchView.as_view(),
        name="catalog-search",
    ),

    path(
        "import/",
        MusicProviderImportView.as_view(),
        name="provider-import",
    ),

    # ============================================================
    # CATALOG
    # ============================================================

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

    # ============================================================
    # COMMUNITY
    # ============================================================

    path(
        "community/posts/",
        CommunityPostListCreateAPIView.as_view(),
        name="community-post-list",
    ),

    path(
        "community/posts/<int:pk>/view/",
        CommunityPostViewAPIView.as_view(),
        name="community-post-view",
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
        "community/posts/<int:pk>/report/",
        CommunityPostReportAPIView.as_view(),
        name="community-post-report",
    ),

    path(
        "community/comments/<int:pk>/report/",
        CommunityPostCommentReportAPIView.as_view(),
        name="community-comment-report",
    ),

    # ============================================================
    # RATINGS
    # ============================================================

    path(
        "songs/<int:pk>/rating/",
        SongRatingAPIView.as_view(),
        name="song-rating",
    ),

    path(
        "albums/<int:pk>/rating/",
        AlbumRatingAPIView.as_view(),
        name="album-rating",
    ),

    # ============================================================
    # FAVORITES
    # ============================================================

    path(
        "songs/<int:pk>/favorite/",
        SongFavoriteAPIView.as_view(),
        name="song-favorite",
    ),

    path(
        "albums/<int:pk>/favorite/",
        AlbumFavoriteAPIView.as_view(),
        name="album-favorite",
    ),

    path(
        "community/posts/<int:pk>/favorite/",
        CommunityPostFavoriteAPIView.as_view(),
        name="community-post-favorite",
    ),

    path(
        "community/favorites/",
        CommunityPostFavoriteListAPIView.as_view(),
        name="community-post-favorites",
    ),

    # ============================================================
    # FOLLOWS
    # ============================================================

    path(
        "artists/<int:pk>/follow/",
        ArtistFollowAPIView.as_view(),
        name="artist-follow",
    ),

    path(
        "users/<int:pk>/follow/",
        UserFollowAPIView.as_view(),
        name="user-follow",
    ),

    # ============================================================
    # LIKES
    # ============================================================

    path(
        "editorial/<int:pk>/like/",
        EditorialArticleLikeAPIView.as_view(),
        name="editorial-article-like",
    ),

    path(
        "community/posts/<int:pk>/like/",
        CommunityPostLikeAPIView.as_view(),
        name="community-post-like",
    ),

    path(
        "editorial/comments/<int:pk>/like/",
        EditorialCommentLikeAPIView.as_view(),
        name="editorial-comment-like",
    ),

    path(
        "community/comments/<int:pk>/like/",
        CommunityPostCommentLikeAPIView.as_view(),
        name="community-comment-like",
    ),

    # ============================================================
    # DISCOVERY
    # ============================================================

    path(
        "discovery/",
        MusicDiscoveryAPIView.as_view(),
        name="discovery",
    ),

    path(
        "discovery/trending/songs/",
        TrendingSongsAPIView.as_view(),
        name="trending-songs",
    ),

    path(
        "discovery/trending/albums/",
        TrendingAlbumsAPIView.as_view(),
        name="trending-albums",
    ),

    path(
        "discovery/trending/artists/",
        TrendingArtistsAPIView.as_view(),
        name="trending-artists",
    ),

    path(
        "discovery/most-discussed/songs/",
        MostDiscussedSongsAPIView.as_view(),
        name="most-discussed-songs",
    ),

    path(
        "discovery/most-discussed/albums/",
        MostDiscussedAlbumsAPIView.as_view(),
        name="most-discussed-albums",
    ),

    path(
        "discovery/most-favorited/songs/",
        MostFavoritedSongsAPIView.as_view(),
        name="most-favorited-songs",
    ),

    path(
        "discovery/most-favorited/albums/",
        MostFavoritedAlbumsAPIView.as_view(),
        name="most-favorited-albums",
    ),

    path(
        "discovery/top-rated/songs/",
        TopRatedSongsAPIView.as_view(),
        name="top-rated-songs",
    ),

    path(
        "discovery/top-rated/albums/",
        TopRatedAlbumsAPIView.as_view(),
        name="top-rated-albums",
    ),

    path(
        "discovery/featured/songs/",
        FeaturedSongsAPIView.as_view(),
        name="featured-songs",
    ),

    path(
        "discovery/featured/albums/",
        FeaturedAlbumsAPIView.as_view(),
        name="featured-albums",
    ),

    path(
        "discovery/featured/artists/",
        FeaturedArtistsAPIView.as_view(),
        name="featured-artists",
    ),

    path(
        "discovery/recent/songs/",
        RecentlyReleasedSongsAPIView.as_view(),
        name="recently-released-songs",
    ),

    path(
        "discovery/recent/albums/",
        RecentlyReleasedAlbumsAPIView.as_view(),
        name="recently-released-albums",
    ),

    # ============================================================
    # EDITORIAL
    # ============================================================

    path(
        "editorial/",
        EditorialArticleListAPIView.as_view(),
        name="editorial-article-list",
    ),

    path(
        "editorial/<slug:slug>/",
        EditorialArticleDetailAPIView.as_view(),
        name="editorial-article-detail",
    ),

    path(
        "editorial/<int:article_id>/comments/",
        EditorialCommentListCreateAPIView.as_view(),
        name="editorial-comment-list",
    ),

    path(
        "editorial/comments/<int:pk>/",
        EditorialCommentDetailAPIView.as_view(),
        name="editorial-comment-detail",
    ),

    path(
        "editorial/<int:pk>/report/",
        EditorialArticleReportAPIView.as_view(),
        name="editorial-article-report",
    ),

    path(
        "editorial/comments/<int:pk>/report/",
        EditorialCommentReportAPIView.as_view(),
        name="editorial-comment-report",
    ),

    # ============================================================
    # FEED INTERACTION ALGORITHM
    # ============================================================

    path(
        "feed/",
        MusicFeedAPIView.as_view(),
        name="music-feed",
    ),

    path(
        "feed/interactions/",
        MusicFeedInteractionAPIView.as_view(),
        name="music-feed-interaction",
    ),

    path(
        "preferences/genres/",
        UserGenrePreferenceListCreateAPIView.as_view(),
        name="genre-preference-list",
    ),

    path(
        "preferences/genres/<int:genre_id>/",
        UserGenrePreferenceDeleteAPIView.as_view(),
        name="genre-preference-delete",
    ),

    path(
        "preferences/genres/set/",
        UserGenrePreferenceSetAPIView.as_view(),
        name="genre-preference-set",
    ),

]