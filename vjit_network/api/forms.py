from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.utils.translation import gettext_lazy as _
from vjit_network.api.models import Notification, UserNotification, User

class NotificationForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = Notification

    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Recipients'),
            is_stacked=False
        )
    )