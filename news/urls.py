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
    path('news/category/politics/', views.politics, name='politics'),
    path('news/category/entertainment/', views.entertainment, name='entertainment'),
    path('news/category/technology/', views.technology, name='technology'),
    path('news/category/lifestyle/', views.lifestyle, name='lifestyle'),
    path('news/category/music-news/', views.music_news, name='music-news'),
    path('news/category/sport/', views.sport, name='sport'),
    path('news/category/event/', views.event, name='event'),
    path('news/category/education/', views.education, name='education'),
    path('news/category/opinion/', views.opinion, name='opinion'),
    path('news/tag/<slug:slug>/', views.news_by_tag, name='news_by_tag'),
    path('category/<slug:slug>/', views.category_news, name='category_news'),
    
]