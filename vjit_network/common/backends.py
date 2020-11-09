from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()

class CustomBackend(ModelBackend): 
    """
	Email Authentication Backend

	Allows a user to sign in using an email/password pair rather than
	a username/password pair.
	"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """ Authenticate a user based on email address as the user name. """
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username and password:
            try:
                if '@' in username:
                    UserModel.USERNAME_FIELD = 'email'
                else:
                    UserModel.USERNAME_FIELD = 'username'
                user = UserModel._default_manager.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                UserModel().set_password(password)
            else:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
        
    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None