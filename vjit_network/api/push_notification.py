from django.conf import settings
from vjit_network.core.models import User
from vjit_network.api.models import Notification, UserNotification
from onesignal import OneSignal, DeviceNotification

ONESINGAL_ANDROID_CHANNEL_ID = settings.ONESINGAL_ANDROID_CHANNEL_ID
ONESIGNAL_APP_ID = settings.ONESIGNAL_APP_ID
ONESIGNAL_REST_API_KEY = settings.ONESIGNAL_REST_API_KEY

notify = OneSignal(ONESIGNAL_APP_ID, ONESIGNAL_REST_API_KEY)


def send(notification: Notification) -> bool:
    """
    send notification instance to all devices of client
    """
    recipients = UserNotification.objects.filter(
        notification=notification, user__is_active=True)
    for recipient in recipients:
        user_instance: User = recipient.user
        notification_payload = recipient.get_payload()
        player_ids = user_instance.devices.filter(
            active=True).values_list('player_id', flat=True)
        device_notification = DeviceNotification(
            include_player_ids=list(player_ids),
            include_external_user_ids=[],
            contents={"en": notification_payload['content']},
            headings={"en": notification_payload['title']},
            url=notification_payload['launch_url'],
            chrome_web_icon=notification_payload['icon'],
            firefox_icon=notification_payload['icon'],
            chrome_web_image=notification_payload['image'],
            small_icon=notification_payload['icon'],
            big_picture=notification_payload['image'],
            priority=10,
            android_channel_id=ONESINGAL_ANDROID_CHANNEL_ID,
        )
        notify.send(device_notification)