from django.core.management.base import BaseCommand
from django.utils import timezone

from flyingfox_app.models import BookingRideSlot


class Command(BaseCommand):

    help = (
        "Mark expired ride slot holds "
        "as expired."
    )


    def handle(self, *args, **options):

        now = timezone.now()

        expired_count = (
            BookingRideSlot.objects
            .filter(
                status="held",
                hold_expires_at__isnull=False,
                hold_expires_at__lte=now,
            )
            .update(
                status="expired",
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Expired {expired_count} "
                    f"ride slot hold(s)."
                )
            )
        )