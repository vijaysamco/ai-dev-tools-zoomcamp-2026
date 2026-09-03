from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create-household/', views.create_household, name='create_household'),
    path('join-household/', views.join_household, name='join_household'),
    path('create-chore/', views.create_chore, name='create_chore'),
    path('chore/<int:chore_id>/edit/', views.edit_chore, name='edit_chore'),
    path('chore/<int:chore_id>/delete/', views.delete_chore, name='delete_chore'),
    path('signup/', views.signup, name='signup'),
]
