from django.urls import path, include
from .views import *

urlpatterns = [
    path("checkouts/download/", DownloadCheckouts.as_view(),
         name="download-checkouts"),
    path("checkouts/upload/", UploadCheckouts.as_view(),
         name="upload-checkouts"),
    path("test/", TestView.as_view(),
             name="test"),
]
