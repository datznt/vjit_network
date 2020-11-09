from django.conf.urls import url
from vjit_network.core import views

app_name = 'core'
urlpatterns = [
    url(r'.well-known/pki-validation/A1F0193986BD8F1AD1188A7DBED26B72.txt',
        views.read_file),
    url(r'dashboard-data', views.AdminDashboardView.as_view())
]
