from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
                url(r'^$', views.index, name='index'),
                url(r'^login/$', views.login, name='login'),
                url(r'^logout/$', views.logout, name='logout'),
                url(r'^setting/$', views.setting, name='setting'),
                url(r'^region/$', views.region, name='region'),
                url(r'^category/$', views.category, name='category'),
                url(r'^country/$', views.country, name='country'),
                url(r'^detail/$', views.detail, name='detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)