from django.urls import path
from me308 import views

urlpatterns = [
    path('', views.home, name='home'),
    path('data/post', views.data_input, name='data-input'),
    path('result', views.data_result, name='data-result'),

]


