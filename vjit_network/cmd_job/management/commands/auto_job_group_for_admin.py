from vjit_network.common.management import LoggerCommand
from vjit_network.core.models import User, GroupUser, Group
import logging

logger = logging.getLogger(__name__)

class Command(LoggerCommand):
    cmd_name = __name__

    def handle(self, *args, **options):
        staffs = User.objects.filter(is_staff=True, is_active=True)

        try:
            for staff in staffs:
                assign_groups = Group.objects.exclude(
                    id__in=staff.group_members.values_list('group', flat=True))

                group_users = map(lambda group: GroupUser(
                    group=group, user=staff, is_active=True), assign_groups)

                GroupUser.objects.bulk_create(list(group_users))
        except Exception as ex:
            logger.exception(ex)