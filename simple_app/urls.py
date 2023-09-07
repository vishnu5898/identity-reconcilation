from django.contrib import admin
from django.urls import path
from simple_app.views import get_contact_data, fill_data

urlpatterns = [
    path('identify', get_contact_data, name="get_contact_data"),
    path('fill', fill_data, name="fill_data"),
]
