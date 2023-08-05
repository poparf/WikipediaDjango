from django.urls import path

from . import views

urlpatterns = [
    path("wiki/random", views.random_view, name="random_view"),
    path("wiki/<str:title>/edit", views.edit, name="edit"),
    path("wiki/create", views.create, name="create"),
    path("wiki/search", views.search, name="search"),
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
]
