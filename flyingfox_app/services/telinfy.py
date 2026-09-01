# flyingfox_app/services/telinfy.py

import requests

from django.conf import settings


def send_otp_sms(
    phone_number,
    otp,
):
    """
    Send login OTP using Telinfy SMS API.
    """

    # =====================================================
    # CONFIG
    # =====================================================

    api_url = getattr(
        settings,
        "TELINFY_SMS_API_URL",
        "",
    )

    api_key = getattr(
        settings,
        "TELINFY_API_KEY",
        "",
    )

    sender_name = getattr(
        settings,
        "TELINFY_SMS_SENDER_NAME",
        "",
    )

    template_id = getattr(
        settings,
        "TELINFY_OTP_TEMPLATE_ID",
        "",
    )

    # =====================================================
    # VALIDATE CONFIG
    # =====================================================

    if not api_url:
        raise RuntimeError(
            "TELINFY_SMS_API_URL is missing."
        )

    if not api_key:
        raise RuntimeError(
            "TELINFY_API_KEY is missing."
        )

    if not sender_name:
        raise RuntimeError(
            "TELINFY_SMS_SENDER_NAME is missing."
        )

    if not template_id:
        raise RuntimeError(
            "TELINFY_OTP_TEMPLATE_ID is missing."
        )

    # =====================================================
    # NORMALIZE PHONE
    # =====================================================

    phone_number = str(
        phone_number
    ).strip()

    phone_digits = "".join(
        char
        for char in phone_number
        if char.isdigit()
    )

    if not phone_digits:
        raise ValueError(
            "Phone number is missing."
        )

    # =====================================================
    # INDIA NUMBER
    #
    # Your login currently stores:
    #
    # +919633390345
    #
    # Telinfy SMS example uses:
    #
    # 9633390345
    #
    # =====================================================

    if (
        phone_digits.startswith("91")
        and
        len(phone_digits) == 12
    ):
        sms_mobile = phone_digits[2:]

    else:
        sms_mobile = phone_digits

    # =====================================================
    # MESSAGE
    #
    # IMPORTANT:
    # Keep wording identical to your approved template.
    # Only replace {#num#} with actual OTP.
    # =====================================================

    sms_message = (
        f"Your Flying Fox login OTP is {otp}. "
        f"It is valid for 5 minutes. "
        f"Do not share this OTP with anyone. "
        f"- Flying Fox Adventure"
    )

    # =====================================================
    # PAYLOAD
    # =====================================================

    payload = {
        "Sender_Name": sender_name,

        "SMS_Message": sms_message,

        "mobile_Number": [
            sms_mobile,
        ],

        "template_id": str(
            template_id
        ),

        "campaign_name": (
            "Flying_Fox_Login_OTP"
        ),
    }

    # =====================================================
    # HEADERS
    # =====================================================

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # =====================================================
    # DEBUG
    #
    # Don't print API key or OTP.
    # =====================================================

    print()
    print("=" * 50)
    print("TELINFY LOGIN OTP REQUEST")
    print("=" * 50)
    print("URL:", api_url)
    print("TO:", sms_mobile)
    print("SENDER:", sender_name)
    print("TEMPLATE:", template_id)
    print("CAMPAIGN: Flying_Fox_Login_OTP")
    print("=" * 50)

    # =====================================================
    # REQUEST
    # =====================================================

    try:

        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=20,
        )

    except requests.RequestException as error:

        raise RuntimeError(
            "Unable to connect to Telinfy SMS API."
        ) from error

    # =====================================================
    # DEBUG RESPONSE
    # =====================================================

    print()
    print("=" * 50)
    print("TELINFY LOGIN OTP RESULT")
    print("=" * 50)
    print(
        "HTTP STATUS:",
        response.status_code,
    )
    print(
        "RESPONSE:",
        response.text[:1000],
    )
    print("=" * 50)
    print()

    # =====================================================
    # HTTP FAILURE
    # =====================================================

    if not response.ok:

        raise RuntimeError(
            "Telinfy OTP request failed. "
            f"HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    # =====================================================
    # JSON
    # =====================================================

    try:

        result = response.json()

    except ValueError:

        raise RuntimeError(
            "Telinfy returned invalid JSON: "
            f"{response.text[:500]}"
        )

    # =====================================================
    # APPLICATION FAILURE
    #
    # Some Telinfy APIs return:
    #
    # {"success": false, ...}
    #
    # Don't assume success only from HTTP 200.
    # =====================================================

    if (
        "success" in result
        and
        result.get("success") is False
    ):

        raise RuntimeError(
            "Telinfy OTP send failed: "
            f"{result}"
        )

    return result






def send_payment_confirmation_sms(
    phone_number,
    booking_id,
    amount,
    visit_date,
):

    api_url = getattr(
        settings,
        "TELINFY_SMS_API_URL",
        "",
    )

    api_key = getattr(
        settings,
        "TELINFY_API_KEY",
        "",
    )

    sender_name = "FLFXAD"

    template_id = "1777178816447707803"

    if not api_url:
        raise RuntimeError(
            "TELINFY_SMS_API_URL is missing."
        )

    if not api_key:
        raise RuntimeError(
            "TELINFY_API_KEY is missing."
        )

    # =====================================================
    # NORMALIZE PHONE NUMBER
    # =====================================================

    phone_number = str(
        phone_number
    ).strip()

    phone_digits = "".join(
        char
        for char in phone_number
        if char.isdigit()
    )

    if not phone_digits:

        raise ValueError(
            "Phone number is missing."
        )

    # +919633390345 -> 9633390345
    if (
        phone_digits.startswith("91")
        and
        len(phone_digits) == 12
    ):

        sms_mobile = phone_digits[2:]

    else:

        sms_mobile = phone_digits

    # =====================================================
    # FORMAT VALUES
    # =====================================================

    booking_id = str(
        booking_id
    ).strip()

    amount = str(
        amount
    ).strip()

    visit_date = str(
        visit_date
    ).strip()

    # =====================================================
    # IMPORTANT:
    # Keep this message exactly matching approved DLT
    # template except variable replacements.
    # =====================================================

    sms_message = (
        f"Payment successful for your Flying Fox Adventure booking. "
        f"Booking ID: {booking_id}, "
        f"Amount: Rs.{amount}, "
        f"Visit Date: {visit_date}. "
        f"Your booking is confirmed. "
        f"Thank you for choosing Flying Fox Adventure."
    )

    payload = {
        "Sender_Name": sender_name,
        "SMS_Message": sms_message,
        "mobile_Number": [
            sms_mobile
        ],
        "template_id": template_id,
        "campaign_name": (
            "Flying_Fox_Payment_Confirmation"
        ),
    }

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print()
    print("=" * 50)
    print("TELINFY PAYMENT SMS REQUEST")
    print("=" * 50)
    print("TO:", sms_mobile)
    print("BOOKING:", booking_id)
    print("AMOUNT:", amount)
    print("VISIT DATE:", visit_date)
    print("=" * 50)

    try:

        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=20,
        )

    except requests.RequestException as error:

        raise RuntimeError(
            "Unable to connect to Telinfy SMS API."
        ) from error

    print()
    print("=" * 50)
    print("TELINFY PAYMENT SMS RESULT")
    print("=" * 50)
    print(
        "HTTP STATUS:",
        response.status_code,
    )
    print(
        "RESPONSE:",
        response.text[:1000],
    )
    print("=" * 50)
    print()

    if not response.ok:

        raise RuntimeError(
            "Telinfy payment SMS failed. "
            f"HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    try:

        result = response.json()

    except ValueError:

        raise RuntimeError(
            "Telinfy returned invalid JSON: "
            f"{response.text[:500]}"
        )

    return result