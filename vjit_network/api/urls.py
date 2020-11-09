from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter
from vjit_network.api import views

app_name = 'vjit_network.api'
router = ExtendedSimpleRouter()

router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'files', views.FileViewSet, basename='files')

router.register(r'users', views.UserViewSet, basename='users')
router.register(r'users-blocks', views.BlockUserViewSet, basename='users-blocks')

router.register(r'posts', views.PostViewSet, basename='posts')
router.register(r'comments', views.CommentViewSet, basename='comments')
router.register(r'views', views.ViewViewSet, basename='views')

router.register(r'groups', views.GroupViewSet, basename='groups')
router.register(r'groups-members', views.GroupUserViewSet, basename='groups-members')

router.register(r'companies', views.CompanyViewSet, basename='companies')

router.register(r'students', views.StudentViewSet, basename='students')

router.register(r'tags', views.TagViewSet, basename='tags')

router.register(r'skills', views.SkillViewSet, basename='skills')

router.register(r'industries', views.IndustryViewSet, basename='industries')

router.register(r'links', views.LinkViewSet, basename='links')

router.register(r'notifications', views.UserNotificationViewSet, basename='notifications')
router.register(r'devices', views.UserDeviceViewSet, basename='devices')

router.register(r'contacts', views.ContactViewSet, basename='contacts')


urlpatterns = router.urls