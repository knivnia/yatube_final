from django.urls import path
from . import views


app_name = 'about'

urlpatterns = [
    path('about/author/', views.AboutAuthorView.as_view(), name='author'),
    path('about/tech/', views.AboutTechView.as_view(), name='tech'),
]
