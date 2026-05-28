from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload'),
    path('records/', views.get_records, name='records'),
    path('records/<int:record_id>/review/', views.review_record, name='review'),
]