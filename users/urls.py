from django.urls import path
from . import views

urlpatterns = [
    path('invitation/<uuid:code>', views.invitation, name='invitation')
]