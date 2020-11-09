from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class MethodSerializerView(object):
    '''
    Utility class for get different serializer class by method.
    For example:
    serializer_classes = {
        ('list', ): MyModelListViewSerializer,
        ('create', 'update', 'partial_update'): MyModelCreateUpdateSerializer
    }
    '''
    serializer_class = None
    serializer_classes = None

    def get_serializer_class(self):
        assert self.serializer_classes is not None, (
            'Expected view %s should contain serializer_classes '
            'to get right serializer class.' %
            (self.__class__.__name__, )
        )
        for actions, serializer_cls in self.serializer_classes.items():
            if self.action in actions:
                return serializer_cls

        raise ImproperlyConfigured(
            "serializer_classes should be a dict mapping.")


class FullUrlQuery(object):
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
