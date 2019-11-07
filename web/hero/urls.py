from django.urls import path
from . import views
app_name = 'hero'
urlpatterns = [
    path('', views.index, name = 'index'),
    path('<herolink>', views.heropage, name = 'heropage'),
    path('<herolink>/talent/<share>', views.herotalentshare, name = 'talentshare'),
]