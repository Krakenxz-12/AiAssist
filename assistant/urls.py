from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/chat/", views.chat, name="chat"),
    path("manifest.json", views.manifest, name="manifest"),
    path("serviceworker.js", views.serviceworker, name="serviceworker"),
]