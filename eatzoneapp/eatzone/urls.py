from django.urls import path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
r.register('categories', views.CategoryViewSet)
r.register('stores', views.StoreViewSet, basename='course')
r.register('dishs', views.DishViewSet, basename='dish')
r.register('users', views.UserViewSet, basename='user')
r.register('comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(r.urls))
]
