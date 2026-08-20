from django.db import migrations


def copy_existing_booking_rides(
    apps,
    schema_editor,
):

    Booking = apps.get_model(
        "flyingfox_app",
        "Booking",
    )

    BookingRideItem = apps.get_model(
        "flyingfox_app",
        "BookingRideItem",
    )

    BookingWeightGroup = apps.get_model(
        "flyingfox_app",
        "BookingWeightGroup",
    )


    for booking in Booking.objects.all():

        if not booking.ride_id:
            continue

        if not booking.ride_price_id:
            continue


        item, created = (
            BookingRideItem.objects.get_or_create(

                booking_id=
                    booking.id,

                ride_id=
                    booking.ride_id,

                defaults={

                    "ride_price_id":
                        booking.ride_price_id,

                    "quantity":
                        booking.quantity,

                    "price_per_person":
                        booking.price_per_person,

                    "offer_id":
                        booking.offer_id,

                    "applied_coupon_code":
                        booking.applied_coupon_code,

                    "discount_amount":
                        booking.discount_amount,

                    "subtotal":
                        booking.subtotal,

                    "total_amount":
                        booking.total_amount,

                    "status":
                        (
                            "checked_in"
                            if booking.status
                            == "checked_in"
                            else "booked"
                        ),

                },
            )
        )


        # ===============================================
        # CONNECT OLD WEIGHT GROUPS TO THE NEW RIDE ITEM
        # ===============================================

        BookingWeightGroup.objects.filter(
            booking_id=
                booking.id,

            booking_item__isnull=
                True,
        ).update(
            booking_item_id=
                item.id
        )


def reverse_copy(
    apps,
    schema_editor,
):

    BookingRideItem = apps.get_model(
        "flyingfox_app",
        "BookingRideItem",
    )

    BookingWeightGroup = apps.get_model(
        "flyingfox_app",
        "BookingWeightGroup",
    )


    BookingWeightGroup.objects.update(
        booking_item=None
    )

    BookingRideItem.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "flyingfox_app",
            "0045_bookingrideitem_and_more",
        ),
    ]

    operations = [

        migrations.RunPython(
            copy_existing_booking_rides,
            reverse_copy,
        ),

    ]