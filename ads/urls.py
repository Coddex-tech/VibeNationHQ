from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('click/<int:ad_id>/', views.ad_click_view, name='ad_click'),
]