from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from flyingfox_app.models import Refund



@transaction.atomic
def mark_refund_processed(
    *,
    razorpay_refund_id,
    gateway_status="processed",
    arn="",
):

    # =====================================================
    # FIND + LOCK REFUND
    # =====================================================

    refund = (
        Refund.objects
        .select_for_update()
        .select_related(
            "booking",
            "payment",
        )
        .filter(
            razorpay_refund_id=
                razorpay_refund_id
        )
        .first()
    )


    if not refund:

        return None


    # =====================================================
    # IDEMPOTENCY
    #
    # Razorpay webhooks can arrive more than once.
    # Never process the same refund twice.
    # =====================================================

    if refund.status == "processed":

        return refund


    booking = refund.booking
    payment = refund.payment


    # =====================================================
    # LOCK BOOKING
    # =====================================================

    booking = (
        Booking.objects
        .select_for_update()
        .get(
            pk=booking.pk
        )
    )


    # =====================================================
    # LOCK PAYMENT
    # =====================================================

    payment = (
        Payment.objects
        .select_for_update()
        .get(
            pk=payment.pk
        )
    )


    # =====================================================
    # LOCK BOOKING RIDE SLOTS
    #
    # These are the capacity reservations belonging
    # to this booking.
    # =====================================================

    booking_slots = list(

        BookingRideSlot.objects
        .select_for_update()
        .filter(
            booking_item__booking=
                booking
        )

    )


    # =====================================================
    # REFUND
    # =====================================================

    refund.status = "processed"

    refund.gateway_status = (
        gateway_status
        or
        "processed"
    )


    if arn:

        refund.arn = arn


    refund.processed_at = (
        timezone.now()
    )


    refund.save(
        update_fields=[
            "status",
            "gateway_status",
            "arn",
            "processed_at",
            "updated_at",
        ]
    )


    # =====================================================
    # PAYMENT
    #
    # Customer receives 90%, therefore technically
    # this is a partial monetary refund.
    #
    # But the entire adventure booking is cancelled.
    # =====================================================

    payment.status = (
        "partially_refunded"
    )


    payment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )


    # =====================================================
    # BOOKING
    # =====================================================

    booking.status = (
        "cancelled"
    )


    booking.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )


    # =====================================================
    # RELEASE RIDE SLOT CAPACITY
    #
    # IMPORTANT:
    #
    # Only confirmed slots consume paid-booking
    # capacity.
    #
    # Once the refund is successfully processed,
    # convert them:
    #
    #     confirmed -> cancelled
    #
    # The availability service will then ignore
    # these rows and the seats become bookable again.
    # =====================================================

    cancelled_slot_count = (

        BookingRideSlot.objects
        .filter(
            booking_item__booking=
                booking,

            status=
                "confirmed",
        )
        .update(
            status=
                "cancelled",

            hold_expires_at=
                None,
        )

    )


    print(
        "BOOKING RIDE SLOTS CANCELLED"
    )

    print(
        "BOOKING:",
        booking.booking_id
    )

    print(
        "SLOT ROWS CHANGED:",
        cancelled_slot_count
    )


    # =====================================================
    # SAFETY CHECK
    #
    # After a completed cancellation there should not
    # be any confirmed slot allocation remaining.
    # =====================================================

    remaining_confirmed_slots = (

        BookingRideSlot.objects
        .filter(
            booking_item__booking=
                booking,

            status=
                "confirmed",
        )
        .count()

    )


    if remaining_confirmed_slots:

        raise ValueError(
            (
                "Refund was processed but "
                f"{remaining_confirmed_slots} "
                "confirmed ride slot allocation(s) "
                "still remain."
            )
        )


    # =====================================================
    # TICKET
    #
    # Booking is cancelled, so the ticket should no
    # longer be considered valid for entry.
    #
    # Keep this section according to the actual fields
    # available in your Ticket model.
    # =====================================================

    ticket = getattr(
        booking,
        "ticket",
        None,
    )


    # If your Ticket model later has an `is_active`
    # field, it can be disabled here.
    #
    # Example:
    #
    # if ticket:
    #
    #     ticket.is_active = False
    #
    #     ticket.save(
    #         update_fields=[
    #             "is_active",
    #         ]
    #     )


    # =====================================================
    # EMAIL
    #
    # Email failure must NOT undo a completed refund.
    # =====================================================

    try:

        if booking.customer_email:

            subject = (
                "Flying Fox Adventures - "
                "Refund Processed"
            )


            message = (
                f"Hello {booking.customer_name},\n\n"

                f"Your cancellation and refund "
                f"have been processed.\n\n"

                f"Booking ID: "
                f"{booking.booking_id}\n"

                f"Amount Paid: "
                f"₹{refund.original_amount}\n"

                f"Cancellation Charge: "
                f"₹{refund.deduction_amount}\n"

                f"Refund Amount: "
                f"₹{refund.refund_amount}\n\n"

                f"Your booking has been cancelled "
                f"and the reserved ride slots have "
                f"been released.\n\n"

                f"The refund has been sent to your "
                f"original payment method. "
                f"Bank processing time may vary.\n\n"

                f"Flying Fox Adventures"
            )


            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [
                    booking.customer_email
                ],
                fail_silently=False,
            )


    except Exception as error:

        # Refund must remain processed even if
        # email temporarily fails.

        print(
            "REFUND EMAIL ERROR:",
            repr(error)
        )


    return refund




@transaction.atomic
def mark_refund_failed(
    *,
    razorpay_refund_id,
    gateway_status="failed",
):

    refund = (
        Refund.objects
        .select_for_update()
        .filter(
            razorpay_refund_id=
                razorpay_refund_id
        )
        .first()
    )


    if not refund:

        return None


    if refund.status == "processed":

        return refund


    refund.status = "failed"

    refund.gateway_status = (
        gateway_status
        or
        "failed"
    )


    refund.save(
        update_fields=[
            "status",
            "gateway_status",
            "updated_at",
        ]
    )


    return refund