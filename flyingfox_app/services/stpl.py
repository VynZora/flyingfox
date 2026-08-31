import requests

from django.conf import settings


# =========================================================
# STPL / SMSGATEWAYHUB OTP SMS
# =========================================================

def send_otp_sms(
    phone_number,
    otp,
):

    # =====================================================
    # CONFIGURATION
    # =====================================================

    api_url = getattr(
        settings,
        "STPL_SMS_API_URL",
        "",
    )

    api_key = getattr(
        settings,
        "STPL_SMS_API_KEY",
        "",
    )

    sender_id = getattr(
        settings,
        "STPL_SMS_SENDER_ID",
        "",
    )

    entity_id = getattr(
        settings,
        "STPL_SMS_ENTITY_ID",
        "",
    )

    dlt_template_id = getattr(
        settings,
        "STPL_SMS_DLT_TEMPLATE_ID",
        "",
    )

    route = getattr(
        settings,
        "STPL_SMS_ROUTE",
        "1",
    )

    # =====================================================
    # VALIDATE CONFIG
    # =====================================================

    required_settings = {
        "STPL_SMS_API_URL": api_url,
        "STPL_SMS_API_KEY": api_key,
        "STPL_SMS_SENDER_ID": sender_id,
        "STPL_SMS_ENTITY_ID": entity_id,
        "STPL_SMS_DLT_TEMPLATE_ID": dlt_template_id,
    }

    missing = [
        name
        for name, value
        in required_settings.items()
        if not value
    ]

    if missing:

        raise RuntimeError(
            "Missing STPL SMS configuration: "
            +
            ", ".join(missing)
        )

    # =====================================================
    # NORMALIZE PHONE
    #
    # STPL expects:
    #
    # 919633390345
    #
    # rather than:
    #
    # +919633390345
    # =====================================================

    phone_number = str(
        phone_number
    ).strip()

    phone_number = "".join(
        char
        for char in phone_number
        if char.isdigit()
    )

    if not phone_number:

        raise ValueError(
            "Phone number is required."
        )

    # =====================================================
    # OTP MESSAGE
    #
    # IMPORTANT:
    # THIS MUST EXACTLY MATCH YOUR APPROVED DLT TEMPLATE.
    # =====================================================

    message_template = getattr(
        settings,
        "STPL_OTP_MESSAGE_TEMPLATE",
        "",
    )

    if not message_template:

        raise RuntimeError(
            "STPL_OTP_MESSAGE_TEMPLATE is missing."
        )

    try:

        message = message_template.format(
            otp=otp
        )

    except KeyError as error:

        raise RuntimeError(
            "STPL_OTP_MESSAGE_TEMPLATE must "
            "contain {otp}."
        ) from error

    # =====================================================
    # STPL PAYLOAD
    # =====================================================

    payload = {

        "APIKey": api_key,

        "senderid": sender_id,

        "channel": "OTP",

        "DCS": "0",

        "flashsms": "0",

        "number": phone_number,

        "text": message,

        "route": route,

        "EntityId": entity_id,

        "dlttemplateid": dlt_template_id,
    }

    # =====================================================
    # DEBUG
    #
    # DO NOT PRINT API KEY OR OTP IN PRODUCTION LOGS.
    # =====================================================

    print(
        "\n========================================"
    )

    print(
        "STPL OTP REQUEST"
    )

    print(
        "TO:",
        phone_number,
    )

    print(
        "SENDER:",
        sender_id,
    )

    print(
        "CHANNEL: OTP"
    )

    print(
        "DLT TEMPLATE:",
        dlt_template_id,
    )

    print(
        "========================================"
    )

    # =====================================================
    # REQUEST
    # =====================================================

    try:

        response = requests.post(
            api_url,
            data=payload,
            timeout=20,
        )

    except requests.RequestException as error:

        raise RuntimeError(
            "Unable to connect to STPL SMS service."
        ) from error

    # =====================================================
    # HTTP ERROR
    # =====================================================

    if not response.ok:

        raise RuntimeError(
            "STPL SMS HTTP error "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    # =====================================================
    # PARSE RESPONSE
    # =====================================================

    try:

        response_data = (
            response.json()
        )

    except ValueError:

        raise RuntimeError(
            "STPL returned an invalid response: "
            f"{response.text[:500]}"
        )

    print(
        "\n========================================"
    )

    print(
        "STPL OTP RESPONSE"
    )

    print(
        "HTTP STATUS:",
        response.status_code,
    )

    print(
        "ERROR CODE:",
        response_data.get(
            "ErrorCode"
        ),
    )

    print(
        "MESSAGE:",
        response_data.get(
            "ErrorMessage"
        ),
    )

    print(
        "JOB ID:",
        response_data.get(
            "JobId"
        ),
    )

    print(
        "========================================\n"
    )

    # =====================================================
    # STPL SUCCESS CHECK
    #
    # Current API documentation shows:
    #
    # ErrorCode = "000"
    # ErrorMessage = "Success"
    # =====================================================

    error_code = str(
        response_data.get(
            "ErrorCode",
            "",
        )
    )

    if error_code != "000":

        raise RuntimeError(
            "STPL OTP failed: "
            f"{response_data.get('ErrorMessage', 'Unknown error')} "
            f"(code {error_code})"
        )

    return response_data