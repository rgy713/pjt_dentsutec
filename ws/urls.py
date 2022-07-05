from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list_country/$', views.list_country, name='ws_list_country'),
    url(r'^list_category/$', views.list_category, name='ws_list_category'),
    url(r'^list_segment/$', views.list_segment, name='ws_list_segment'),
    url(r'^list_company/$', views.list_company, name='ws_list_company'),
    url(r'^list_client/$', views.list_client, name='ws_list_client'),
    url(r'^list_segment_client/$', views.list_segment_client, name='ws_list_segment_client'),
    url(r'^list_media/$', views.list_media, name='ws_list_media'),
    url(r'^list_project/$', views.list_project, name='ws_list_project'),
    url(r'^get_project/$', views.get_project, name='ws_get_project'),
    url(r'^update_user_setting/$', views.update_user_setting, name='ws_update_user_setting'),
    url(r'^get_user_setting/$', views.get_user_setting, name='ws_get_user_setting'),
]