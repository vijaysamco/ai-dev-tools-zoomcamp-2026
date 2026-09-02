from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create-household/', views.create_household, name='create_household'),
    path('join-household/', views.join_household, name='join_household'),
    path('signup/', views.signup, name='signup'),
]
