from django.urls import path, include, re_path
from study_groups import views

app_name = 'study_groups'

urlpatterns = [
    path('', views.MyGroupsView.as_view(), name='my_groups')
]