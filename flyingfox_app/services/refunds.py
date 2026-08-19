from decimal import Decimal, ROUND_HALF_UP

import razorpay

from django.conf import settings


def create_razorpay_refund(
    *,
    payment_id,
    refund_amount,
    booking_id,
    refund_id,
):

    # =====================================================
    # VALIDATE PAYMENT ID
    # =====================================================

    if not payment_id:

        raise ValueError(
            "Razorpay payment ID is missing."
        )


    # =====================================================
    # CONVERT RUPEES → PAISE
    #
    # Example:
    # ₹2160.00 → 216000
    # =====================================================

    amount = Decimal(
        str(refund_amount)
    )


    amount_paise = int(

        (
            amount
            *
            Decimal("100")
        ).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )

    )


    if amount_paise <= 0:

        raise ValueError(
            "Refund amount must be greater than zero."
        )


    # =====================================================
    # RAZORPAY CLIENT
    # =====================================================

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )


    # =====================================================
    # CREATE REFUND
    # =====================================================

    refund_data = {

        "amount":
            amount_paise,

        "speed":
            "normal",

        "receipt":
            f"refund-{str(refund_id)[:20]}",

        "notes": {

            "booking_id":
                str(booking_id),

            "refund_id":
                str(refund_id),

            "source":
                "Flying Fox Adventures",

        },
    }


    return client.payment.refund(
        payment_id,
        refund_data,
    )