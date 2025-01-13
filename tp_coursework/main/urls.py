from django.urls import path
from . import views

urlpatterns = [
    path('', views.events_list, name='events_list'),
    path('about-us', views.about),
    path('register/', views.register_participant, name='register_participant'),
    path('get_participants/<int:event_id>/', views.get_participants, name='get_participants'),
    path('get_statistics/<int:event_id>/', views.event_statistics, name='get_statistics'),
    path('export_participants_json/<int:event_id>/', views.export_participants_json, name='export_participants_json'),
    path('export_participants_csv/<int:event_id>/', views.export_participants_csv, name='export_participants_csv'),
]
