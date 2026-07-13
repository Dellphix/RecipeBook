from django.urls import path

from . import views


app_name = "recipes"
urlpatterns = [
    path("", views.PublicIndexView.as_view(), name="index"),
    path("my-recipes/", views.UserIndexView.as_view(), name="my_recipes"),
    path("<uuid:uuid>/", views.DetailView.as_view(), name="detail"),
    path("<uuid:uuid>/edit", views.UpdateView.as_view(), name="update"),
    path("<uuid:uuid>/delete", views.DeleteView.as_view(), name="delete"),
    path("create", views.CreateView.as_view(), name="create"),
    path("ajax-ingredient", views.ajax_ingredient, name="ajax_ingredient"),
]