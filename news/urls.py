from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
     path('', views.homepage, name='homepage'),
     path('news/', views.news_home, name='news_home'),
     path('news/<slug:slug>/', views.news_detail, name='news_details'),
     path('news/<int:news_id>/load-comments/',
         views.load_more_comments, name='load_more_comments'), # comment

     path('load-more-replies/<int:comment_id>/',
         views.load_more_replies, name='load_more_news_replies'), # reply

     path('news/category/politics/', views.politics_frontend, name='politics'),
     path('news/api/politics/', views.politics, name='politics_api_feed'),

     path('news/category/entertainment/', views.entertainment_frontend, name='entertainment'),
     path('news/api/entertainment/', views.entertainment, name='entertainment_api_feed'),

     path('news/category/technology/', views.technology_frontend, name='technology'),
     path('news/api/technology/', views.technology, name='technology_api_feed'),

     path('news/category/lifestyle/', views.lifestyle_frontend, name='lifestyle'),
     path('news/api/lifestyle/', views.lifestyle, name='lifestyle_api_feed'),

     path('news/category/music-news/', views.music_news_frontend, name='music_news'),
     path('news/api/music-news/', views.music_news, name='music_news_api_feed'),

     path('news/category/sports/', views.sports_frontend, name='sports'),
     path('news/api/sports/', views.sports, name='sports_api_feed'),

     path('news/category/events/', views.events_frontend, name='events'),
     path('news/api/events/', views.events, name='events_api_feed'),

     path('news/category/education/', views.education_frontend, name='education'),
     path('news/api/education/', views.education, name='education_api_feed'),

     path('news/category/opinion/', views.opinion_frontend, name='opinion'),
     path('news/api/opinion/', views.opinion, name='opinion_api_feed'),

     path('news/tags/<slug:tag_slug>/', views.news_by_tag_frontend, name='news_by_tag'),
     path('news/api/tags/<slug:tag_slug>/', views.news_by_tag, name='news_by_tag_api_feed'),

     path('category/<slug:slug>/', views.category_news, name='category_news'),
    
]