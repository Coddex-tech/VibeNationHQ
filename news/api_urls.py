from django.urls import path
from news.api_views import (
    HomePageAPIView,
    NewsHomeAPIView,
    NewsDetailAPIView,
    SidebarDataAPIView,
    RecentSongsAPIView,
    ArticleCommentsChunkAPIView,
    CommentRepliesChunkAPIView,
    CategoryNewsAPIView,
    NewsByTagAPIView,
    CategoryHomeAPIView
    )

app_name = 'news_api'

urlpatterns = [
    # HOMEPAGE
    path(
        "homepage/",
        HomePageAPIView.as_view(),
        name="news-home-api"
    ),

    # NEWS HOMEPAGE
    path(
        "news-home/",
        NewsHomeAPIView.as_view(),
        name="news-home-api",
    ),

    # CATEGORY NEWS
    path(
        "category/<slug:slug>/",
        CategoryNewsAPIView.as_view(),
        name="news-category-api",
    ),

    # NEWS BY TAG
    path(
        "tag/<slug:slug>/",
        NewsByTagAPIView.as_view(),
        name="news-by-tag-api",
    ),

    path(
        "<slug:slug>/",
        CategoryHomeAPIView.as_view(),
        name="category-home-api",
    ),

    # Fetch main article details by slug
     path('article/<slug:slug>/', 
         NewsDetailAPIView.as_view(), 
         name='api_news_detail'),

    # Fetch layout sidebar aggregation (Trending + Categories)
     path('layout/sidebar/', 
         SidebarDataAPIView.as_view(), 
         name='api_sidebar_data'),

    # Fetch layout music break grid component
     path('layout/recent-songs/', 
         RecentSongsAPIView.as_view(), 
         name='api_recent_songs'),

     # Comment chunk
     path('<slug:slug>/comments/',
          ArticleCommentsChunkAPIView.as_view(),
          name='api_comments_chunk'),
     
     # reply chunk
     path('comments/<int:comment_id>/replies/',
          CommentRepliesChunkAPIView.as_view(),
          name='api_replies_chunk'),
]