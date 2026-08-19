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
    # FIND REFUND
    # =====================================================

    refund = (
        Refund.objects
        .select_for_update()
        .select_related(
            "booking",
            "payment",
        )
        .filter(
            razorpay_refund_id=razorpay_refund_id
        )
        .first()
    )


    if not refund:

        return None


    # =====================================================
    # IDEMPOTENCY
    #
    # Webhook can be delivered more than once.
    # Do not process twice.
    # =====================================================

    if refund.status == "processed":

        return refund


    booking = refund.booking
    payment = refund.payment


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
    # Your policy returns 90%, so technically this is
    # a partial refund.
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
    # TICKET
    #
    # If your Ticket model has an active/used field,
    # invalidate it here.
    # =====================================================

    ticket = getattr(
        booking,
        "ticket",
        None,
    )


    # Example only:
    #
    # if ticket:
    #     ticket.is_active = False
    #     ticket.save(update_fields=["is_active"])


    # =====================================================
    # EMAIL
    # =====================================================

    try:

        if booking.customer_email:

            subject = (
                "Flying Fox Adventures - Refund Processed"
            )


            message = (
                f"Hello {booking.customer_name},\n\n"
                f"Your cancellation and refund have been processed.\n\n"
                f"Booking ID: {booking.booking_id}\n"
                f"Amount Paid: ₹{refund.original_amount}\n"
                f"Cancellation Charge: ₹{refund.deduction_amount}\n"
                f"Refund Amount: ₹{refund.refund_amount}\n\n"
                f"The refund has been sent to your original "
                f"payment method. Bank processing time may vary.\n\n"
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