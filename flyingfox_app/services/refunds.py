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

    payment_id = str(
        payment_id or ""
    ).strip()


    if not payment_id:

        raise ValueError(
            "Razorpay payment ID is missing."
        )


    # Optional additional validation.
    #
    # Razorpay payment IDs normally begin with "pay_".

    if not payment_id.startswith("pay_"):

        raise ValueError(
            "Invalid Razorpay payment ID."
        )


    # =====================================================
    # VALIDATE REFUND ID
    # =====================================================

    if not refund_id:

        raise ValueError(
            "Local refund ID is missing."
        )


    # =====================================================
    # VALIDATE BOOKING ID
    # =====================================================

    if not booking_id:

        raise ValueError(
            "Booking ID is missing."
        )


    # =====================================================
    # CONVERT REFUND AMOUNT
    # =====================================================

    try:

        amount = Decimal(
            str(refund_amount)
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    except Exception as error:

        raise ValueError(
            "Invalid refund amount."
        ) from error


    # =====================================================
    # AMOUNT MUST BE POSITIVE
    # =====================================================

    if amount <= Decimal("0.00"):

        raise ValueError(
            "Refund amount must be greater than zero."
        )


    # =====================================================
    # RUPEES → PAISE
    #
    # ₹2160.00
    #
    # becomes:
    #
    # 216000
    # =====================================================

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
            "Refund amount in paise must be greater than zero."
        )


    # =====================================================
    # RAZORPAY SETTINGS CHECK
    # =====================================================

    key_id = getattr(
        settings,
        "RAZORPAY_KEY_ID",
        "",
    )


    key_secret = getattr(
        settings,
        "RAZORPAY_KEY_SECRET",
        "",
    )


    if (
        not key_id
        or
        not key_secret
    ):

        raise ValueError(
            "Razorpay credentials are not configured."
        )


    # =====================================================
    # RAZORPAY CLIENT
    # =====================================================

    client = razorpay.Client(
        auth=(
            key_id,
            key_secret,
        )
    )


    # =====================================================
    # UNIQUE RECEIPT
    #
    # Keep this stable for this Refund record.
    #
    # IMPORTANT:
    # Do not generate a new random value on every retry.
    # =====================================================

    receipt = (
        f"refund-{str(refund_id)}"
    )


    # Razorpay allows a receipt for your internal reference.
    # Keep it reasonably short.

    receipt = receipt[:40]


    # =====================================================
    # CREATE REFUND DATA
    # =====================================================

    refund_data = {

        "amount":
            amount_paise,

        # Normal refund:
        # usually reaches the customer's original
        # payment method in several business days.

        "speed":
            "normal",

        "receipt":
            receipt,

        "notes": {

            # Useful for webhook lookup / reconciliation.

            "booking_id":
                str(booking_id),

            "refund_id":
                str(refund_id),

            "source":
                "Flying Fox Adventures",

        },
    }


    # =====================================================
    # CREATE RAZORPAY REFUND
    # =====================================================

    razorpay_refund = (
        client.payment.refund(
            payment_id,
            refund_data,
        )
    )


    # =====================================================
    # BASIC RESPONSE VALIDATION
    # =====================================================

    if not isinstance(
        razorpay_refund,
        dict,
    ):

        raise RuntimeError(
            "Invalid response received from Razorpay."
        )


    if not razorpay_refund.get(
        "id"
    ):

        raise RuntimeError(
            "Razorpay refund ID was not returned."
        )


    # =====================================================
    # RETURN COMPLETE RAZORPAY RESPONSE
    # =====================================================

    return razorpay_refund