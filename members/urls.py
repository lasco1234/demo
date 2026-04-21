from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main.html'),
    path('members/', views.members, name='members'),
    path('details/<int:id>/', views.details, name='details'),
    path('myfirst/', views.myfirst, name='myfirst'),
    path('testing/', views.testing, name='testing',)
]