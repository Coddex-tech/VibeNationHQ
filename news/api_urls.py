from django.urls import path
from news.api_views import (
    NewsHomeAPIView,
    NewsDetailAPIView,
    SidebarDataAPIView,
    RecentSongsAPIView,
    ArticleCommentsChunkAPIView,
    CommentRepliesChunkAPIView,
    CategoryNewsAPIView,
    NewsByTagAPIView,
    EntertainmentAPIView,
    PoliticsAPIView,
    LifestyleAPIView,
    TechnologyAPIView,
    MusicNewsAPIView,
    SportsAPIView,
    EventsAPIView,
    EducationAPIView,
    OpinionAPIView
    )

app_name = 'news_api'

urlpatterns = [
    # HOMEPAGE
    path(
        "home/",
        NewsHomeAPIView.as_view(),
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

    # ENTERTAINMENT
    path(
        "entertainment/",
        EntertainmentAPIView.as_view(),
        name="entertainment-api"
    ),

    # POLITICS
    path(
        "politics/",
        PoliticsAPIView.as_view(),
        name="politics-api"
    ),

    # LIFESTYLE
    path(
        "lifestyle/",
        LifestyleAPIView.as_view(),
        name="lifestyle-api"
    ),

    # TECHNOLOGY
    path(
        "technology/",
        TechnologyAPIView.as_view(),
        name="technology-api"
    ),

    # MUSIC NEWS
    path(
        "music-news/",
        MusicNewsAPIView.as_view(),
        name="music-news-api"
    ),

    # SPORTS
    path(
        "sports/",
        SportsAPIView.as_view(),
        name="sports-api"
    ),

    # EVENTS
    path(
        "events/",
        EventsAPIView.as_view(),
        name="events-api"
    ),

    # EDUCATION
    path(
        "education/",
        EducationAPIView.as_view(),
        name="education-api"
    ),

    # OPINION
    path(
        "music-news/",
        OpinionAPIView.as_view(),
        name="opinion-api"
    ),

    # Fetch main article details by slug
     path('<slug:slug>/', 
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