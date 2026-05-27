from django.urls import path

from . import views


app_name = "recipes"
urlpatterns = [
    # ex: /recipes/
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/edit", views.UpdateView.as_view(), name="update"),
    path("<int:pk>/delete", views.DeleteView.as_view(), name="delete"),
    path("create", views.CreateView.as_view(), name="create"),
]