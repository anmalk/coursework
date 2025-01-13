from django.urls import path
from . import views

urlpatterns = [
    path('', views.events_list, name='events_list'),
    path('about-us', views.about),
    path('register/', views.register_participant, name='register_participant'),

]
