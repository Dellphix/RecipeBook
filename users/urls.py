from django.urls import path
from . import views

urlpatterns = [
    # path('logout/', views.sign_out, name='logout'),
    path('invitation/<uuid:code>', views.invitation, name='invitation')
]