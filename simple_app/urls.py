from django.contrib import admin
from django.urls import path
from simple_app.views import get_contact_data

urlpatterns = [
    path('identify', get_contact_data, name="get_contact_data"),
]
