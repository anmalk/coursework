from django.urls import path
from . import views

urlpatterns = [
    path('', views.events_list, name='events_list'),
    path('register/', views.register_participant, name='register_participant'),
    path('get_participants/<int:event_id>/', views.get_participants, name='get_participants'),
    path('get_statistics/<int:event_id>/', views.event_statistics, name='get_statistics'),
    path('export/<int:event_id>/<str:export_format>/', views.export_participants, name='export_participants'),

]
