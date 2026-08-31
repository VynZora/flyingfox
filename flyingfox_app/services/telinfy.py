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