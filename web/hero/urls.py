from django.urls import path
from . import views
app_name = 'hero'
urlpatterns = [
    path('', views.index, name = 'index'),
    path('<herolink>', views.heropage, name = 'heropage'),
    path('<herolink>/skin', views.heroskin, name = 'heroskin'),
    path('<herolink>/voiceline', views.herovoices, name = 'herovoice'),
    path('<herolink>/talent', views.herotalent, name = 'herotalent'),
    path('<herolink>/talent/<share>', views.herotalentshare, name = 'talentshare'),
]