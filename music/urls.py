from django.urls import path
from . import views

app_name = "music"
urlpatterns = [
    path('', views.music, name="music_nav"),
    path("songs/<slug:slug>/", views.song_detail, name="song_detail"), # for song detail page
    path('song/<int:song_id>/load-comments/',
         views.load_more_music_comments, name='load_more_music_comments'), # comment
    path('load-music-replies/<int:comment_id>/',
         views.load_more_music_replies, name='load_more_music_replies'), # Reply
    path("music/mixtape/<slug:slug>", views.song_detail, name="mixtapes"), # for mixtapes detail page same with song
    path('search/', views.search, name='search'),
    path('newest-song/', views.latest_music, name="newest-song"),
    path('gospel-song/', views.gospel, name="gospel-song"),
    path('mixtape/', views.mixtape, name="mixtape"),
    path('trending/', views.trending_song, name="trending"),
    path('download/<slug:slug>/', views.download_song, name="download_song"),
    path('africa/', views.african_music, name="african-song"),
    path('albums/', views.album, name="albums"),
    path('album/<slug:slug>/', views.album_detail, name='album_detail'),
    path('tag/<slug:tag_slug>/', views.songs_by_tag, name='songs_by_tag'),
]