from django.db import models
from django.db.models.functions import Concat, Coalesce, Trim, NullIf
from django.contrib.auth import models as auth_models
from django.core.cache import cache

class UserManager(auth_models.UserManager):
    pass
    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     # =====================================
    #     # REDUCE QUERY SET
    #     # =====================================
    #     fullname = Trim(Concat(models.F('last_name'),
    #                            models.Value(' '), models.F('first_name')))
    #     fullname_or_username = Coalesce(
    #         NullIf(fullname, models.Value('')), models.F('username'))

    #     return qs.annotate(fullname=fullname_or_username)


class BlockUserManager(models.Manager):

    def as_user(self, user, to_list_user=False):
        """
        Find all user blocked by me
        """
        cache_key = self._cache_key(user, to_list_user)
        qs = cache.get(cache_key)
        if not qs:
            qs = super().get_queryset().filter(create_by=user, is_active=True)
            if to_list_user:
                qs = qs.values_list('create_by', flat=True)
            cache.set(cache_key, qs, 60)
        return qs

    def _cache_key(self, user, to_list_user=False):
        return '_'.join([
            user.cache_key,
            'blocklist',
            'flat' if to_list_user else 'noflat'
        ])
