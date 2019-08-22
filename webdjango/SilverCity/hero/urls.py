from django.urls import path
from . import views
app_name = 'hero'
urlpatterns = [
    path('', views.index, name = 'index'),
    path('<heroname>', views.heropage, name = 'heropage')
]