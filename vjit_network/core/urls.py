from django.conf.urls import url
from vjit_network.core import views

app_name = 'core'
urlpatterns = [
    url(r'.well-known/pki-validation/A0A183D1A0C45A0E1E7DCB87545B2C2E.txt',
        views.read_file),
    url(r'admin/dashboard-data', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    url(r'admin/student-creation', views.StudentCreateView.as_view(), name='student_creation'),
]