import secrets
from datetime import timedelta

from django.utils import timezone
import requests
from django.conf import settings

from flyingfox import settings

from .models import Booking, OTPVerification
from .services.telinfy import send_otp_sms


def generate_otp():
    return str(
        secrets.randbelow(900000) + 100000
    )


def send_otp(phone_number):

    # Generate OTP
    otp = generate_otp()

    # Expire previous unused OTPs
    OTPVerification.objects.filter(
        phone_number=phone_number,
        is_verified=False,
    ).update(
        expires_at=timezone.now()
    )

    # Create new OTP
    otp_verification = OTPVerification.objects.create(
        phone_number=phone_number,
        otp=otp,
        expires_at=timezone.now() + timedelta(minutes=5),
    )

    # Send OTP through Telinfy SMS
    try:

        response = send_otp_sms(
            phone_number,
            otp
        )

    except Exception:

        otp_verification.delete()

        raise

    return otp_verification, response


def verify_otp(phone_number, entered_otp):

    otp_record = (
        OTPVerification.objects
        .filter(
            phone_number=phone_number,
            is_verified=False,
        )
        .order_by("-created_at")
        .first()
    )

    # No OTP
    if not otp_record:

        return (
            False,
            "No OTP found. Please request a new OTP."
        )

    # Expired
    if timezone.now() > otp_record.expires_at:

        return (
            False,
            "OTP has expired. Please request a new OTP."
        )

    # Too many attempts
    if otp_record.attempts >= 5:

        return (
            False,
            "Too many incorrect attempts. Please request a new OTP."
        )

    # Wrong OTP
    if otp_record.otp != str(entered_otp):

        otp_record.attempts += 1

        otp_record.save(
            update_fields=["attempts"]
        )

        return (
            False,
            "Invalid OTP."
        )

    # Correct OTP
    otp_record.is_verified = True

    otp_record.save(
        update_fields=["is_verified"]
    )

    return (
        True,
        "OTP verified successfully."
    )







# def send_ticket_whatsapp(request, ticket):
#     """
#     Send booking confirmation through Telinfy WhatsApp API.

#     Template:
#         booking_confirmations_v2

#     Variables:
#         {{1}} Customer name
#         {{2}} Ticket number
#         {{3}} Booking ID
#         {{4}} Visit date
#         {{5}} Ride summary
#         {{6}} Total riders
#         {{7}} Total amount
#     """

#     # =====================================================
#     # BOOKING
#     # =====================================================

#     booking = (
#         Booking.objects
#         .prefetch_related(
#             "ride_items__ride",
#             "ride_items__weight_groups",
#         )
#         .get(pk=ticket.booking.pk)
#     )

#     # =====================================================
#     # CUSTOMER PHONE
#     # =====================================================

#     if not booking.customer_phone:
#         print("WHATSAPP ERROR: Customer phone is empty.")
#         return False

#     phone = (
#         booking.customer_phone
#         .strip()
#         .replace(" ", "")
#         .replace("-", "")
#         .replace("(", "")
#         .replace(")", "")
#     )

#     # 9633390345 -> 919633390345
#     if len(phone) == 10 and phone.isdigit():
#         phone = f"91{phone}"

#     # 919633390345
#     elif len(phone) == 12 and phone.startswith("91") and phone.isdigit():
#         pass

#     # +919633390345 -> 919633390345
#     elif len(phone) == 13 and phone.startswith("+91") and phone[1:].isdigit():
#         phone = phone[1:]

#     else:
#         print("WHATSAPP ERROR: Invalid phone number:", phone)
#         return False

#     # IMPORTANT:
#     # Telinfy API accepts the phone with +91.
#     telinfy_phone = f"+{phone}"

#     # =====================================================
#     # TELINFY API KEY
#     # =====================================================

#     api_key = getattr(
#         settings,
#         "TELINFY_API_KEY",
#         "",
#     )

#     if not api_key:
#         print("WHATSAPP ERROR: TELINFY_API_KEY is missing.")
#         return False

#     # =====================================================
#     # RIDE SUMMARY
#     # =====================================================

#     ride_lines = []

#     for item in booking.ride_items.all():

#         if not item.ride:
#             continue

#         ride_lines.append(
#             f"{item.ride.name} - {item.quantity} rider(s)"
#         )

#     ride_summary = ", ".join(ride_lines)

#     if not ride_summary:
#         ride_summary = (
#             "Adventure details are included "
#             "in your PDF ticket."
#         )

#     # =====================================================
#     # TEMPLATE VALUES
#     # =====================================================

#     customer_name = (
#         booking.customer_name
#         or ""
#     )

#     ticket_number = (
#         ticket.ticket_number
#         or ""
#     )

#     booking_id_value = str(
#         booking.booking_id
#     )

#     visit_date = (
#         booking.booking_date.strftime("%d-%m-%Y")
#         if booking.booking_date
#         else ""
#     )

#     total_riders = str(
#         booking.quantity
#     )

#     total_amount = str(
#         booking.total_amount
#     )

#     # =====================================================
#     # TELINFY OFFICIAL TEMPLATE API
#     # =====================================================

#     url = (
#     "https://hub.telinfy.com/unified/developer/"
#     "api/v1/whatsapp/campaigns/send"
#     )

#     # =====================================================
#     # HEADERS
#     # =====================================================

#     headers = {
#          "x-api-key": api_key,
#          "Content-Type": "application/json",
#     }

#     # =====================================================
#     # PAYLOAD
#     # =====================================================
#     payload = {
#     "phoneNumber": telinfy_phone,

#     "template": {
#         "name": "booking_confirmations_v2",

#         "language": {
#             "code": "en",
#         },

#         "components": [
#             {
#                 "type": "body",

#                 "parameters": [
#                     {
#                         "type": "text",
#                         "text": str(customer_name),
#                     },
#                     {
#                         "type": "text",
#                         "text": str(ticket_number),
#                     },
#                     {
#                         "type": "text",
#                         "text": str(booking_id_value),
#                     },
#                     {
#                         "type": "text",
#                         "text": str(visit_date),
#                     },
#                     {
#                         "type": "text",
#                         "text": str(ride_summary),
#                     },
#                     {
#                         "type": "text",
#                         "text": str(total_riders),
#                     },
#                     {
#                         "type": "text",
#                         "text": str(total_amount),
#                     },
#                 ],
#             }
#         ],
#     },
# }
# # =====================================================
# # DEBUG
# # =====================================================

#     print("\n========================================")
#     print("TELINFY WHATSAPP REQUEST")
#     print("========================================")
#     print("URL:", url)
#     print("TO:", telinfy_phone)
#     print("TEMPLATE:", "booking_confirmations_v2")
#     print("LANGUAGE:", "en")

#     parameters = payload["template"]["components"][0]["parameters"]

#     print("PARAMETER COUNT:", len(parameters))
#     print("PARAMETERS:")

#     for index, parameter in enumerate(
#         parameters,
#         start=1,
#         ):
#         print(
#            f"  {{{{{index}}}}}:",
#            parameter["text"],
#         )

#     print("========================================")

#     # =====================================================
#     # SEND
#     # =====================================================

#     try:

#         response = requests.post(
#             url,
#             headers=headers,
#             json=payload,
#             timeout=30,
#         )

#         print("\n========================================")
#         print("TELINFY WHATSAPP RESULT")
#         print("========================================")
#         print("HTTP STATUS:", response.status_code)
#         print("RESPONSE:", response.text)
#         print("========================================\n")

#         # =================================================
#         # PARSE RESPONSE
#         # =================================================

#         try:
#             response_data = response.json()
#         except ValueError:
#             response_data = {}

#         # =================================================
#         # SUCCESS
#         # =================================================

#         if (
#             response.ok
#             and response_data.get("success") is True
#         ):

#             ticket.whatsapp_sent = True

#             ticket.save(
#                 update_fields=[
#                     "whatsapp_sent"
#                 ]
#             )

#             print(
#                 "WHATSAPP ACCEPTED BY TELINFY"
#             )

#             print(
#                 "RECORD ID:",
#                 response_data.get("data", {}).get(
#                     "recordId"
#                 )
#             )

#             print(
#                 "QUEUE STATUS:",
#                 response_data.get("data", {}).get(
#                     "queueStatus"
#                 )
#             )

#             return True

#         # =================================================
#         # FAILED
#         # =================================================

#         print(
#             "WHATSAPP SEND FAILED"
#         )

#         return False

#     except requests.RequestException as error:

#         print("\n========================================")
#         print("TELINFY WHATSAPP REQUEST ERROR")
#         print("========================================")
#         print("TYPE:", type(error).__name__)
#         print("ERROR:", repr(error))
#         print("========================================\n")

#         return False





def send_ticket_whatsapp(request, ticket):
    """
    Send booking confirmation with QR code image
    through Telinfy WhatsApp API.

    Template header:
        IMAGE -> ticket QR code

    Body variables:
        {{1}} Customer name
        {{2}} Ticket number
        {{3}} Booking ID
        {{4}} Visit date
        {{5}} Ride summary
        {{6}} Total riders
        {{7}} Total amount
    """

    # =====================================================
    # BOOKING
    # =====================================================

    booking = (
        Booking.objects
        .prefetch_related(
            "ride_items__ride",
            "ride_items__weight_groups",
        )
        .get(pk=ticket.booking.pk)
    )

    # =====================================================
    # CUSTOMER PHONE
    # =====================================================

    if not booking.customer_phone:
        print(
            "WHATSAPP ERROR: Customer phone is empty."
        )
        return False

    phone = (
        booking.customer_phone
        .strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    # -----------------------------------------------------
    # NORMALIZE PHONE
    # -----------------------------------------------------

    # 9633390345 -> 919633390345
    if len(phone) == 10 and phone.isdigit():
        phone = f"91{phone}"

    # 919633390345
    elif (
        len(phone) == 12
        and phone.startswith("91")
        and phone.isdigit()
    ):
        pass

    # +919633390345 -> 919633390345
    elif (
        len(phone) == 13
        and phone.startswith("+91")
        and phone[1:].isdigit()
    ):
        phone = phone[1:]

    else:
        print(
            "WHATSAPP ERROR: Invalid phone number:",
            phone,
        )
        return False

    telinfy_phone = f"+{phone}"

    # =====================================================
    # TELINFY SETTINGS
    # =====================================================

    api_key = getattr(
        settings,
        "TELINFY_API_KEY",
        "",
    )

    base_url = getattr(
        settings,
        "TELINFY_BASE_URL",
        "https://hub.telinfy.com/unified/developer",
    )

    template_name = getattr(
        settings,
        "TELINFY_WHATSAPP_TEMPLATE",
        "booking_confirmation_qr",
    )

    language_code = getattr(
        settings,
        "TELINFY_WHATSAPP_LANGUAGE",
        "en",
    )

    if not api_key:
        print(
            "WHATSAPP ERROR: "
            "TELINFY_API_KEY is missing."
        )
        return False

    # =====================================================
    # CHECK QR IMAGE
    # =====================================================

    if not ticket.qr_image:
        print(
            "WHATSAPP ERROR: "
            "Ticket QR image is missing."
        )
        return False

    if not ticket.qr_image.name:
        print(
            "WHATSAPP ERROR: "
            "Ticket QR image has no file name."
        )
        return False

    # =====================================================
    # BUILD PUBLIC QR URL
    # =====================================================

    try:

        qr_relative_url = ticket.qr_image.url

        public_base_url = getattr(
          settings,
          "PUBLIC_BASE_URL",
          "",
        )

        if not public_base_url:

           print(
            "WHATSAPP ERROR: "
            "PUBLIC_BASE_URL is missing."
            )

           return False

        qr_url = (
          f"{public_base_url.rstrip('/')}"
          f"{qr_relative_url}"
        )

    except Exception as error:

        print(
         "WHATSAPP ERROR: "
        "Unable to build QR URL."
        )

        print(
        "ERROR:",
        repr(error),
        )

        return False

    # =====================================================
    # VALIDATE PUBLIC URL
    # =====================================================

    if (
        "localhost" in qr_url.lower()
        or "127.0.0.1" in qr_url
    ):

        print(
            "WHATSAPP ERROR: "
            "QR URL is localhost and cannot "
            "be downloaded by Telinfy/WhatsApp."
        )

        print(
            "QR URL:",
            qr_url,
        )

        return False

    # =====================================================
    # RIDE SUMMARY
    # =====================================================

    ride_lines = []

    for item in booking.ride_items.all():

        if not item.ride:
            continue

        ride_lines.append(
            f"{item.ride.name} - "
            f"{item.quantity} rider(s)"
        )

    ride_summary = ", ".join(
        ride_lines
    )

    if not ride_summary:

        ride_summary = (
            "Adventure details are included "
            "in your PDF ticket."
        )

    # =====================================================
    # TEMPLATE VALUES
    # =====================================================

    customer_name = (
        booking.customer_name
        or ""
    )

    ticket_number = str(
        ticket.ticket_number
        or ""
    )

    booking_id_value = str(
        booking.booking_id
    )

    visit_date = (
        booking.booking_date.strftime(
            "%d-%m-%Y"
        )
        if booking.booking_date
        else ""
    )

    total_riders = str(
        booking.quantity
    )

    total_amount = str(
        booking.total_amount
    )

    # =====================================================
    # TELINFY URL
    # =====================================================

    url = (
        f"{base_url.rstrip('/')}"
        "/api/v1/whatsapp/campaigns/send"
    )

    # =====================================================
    # HEADERS
    # =====================================================

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    # =====================================================
    # BODY PARAMETERS
    # =====================================================

    body_parameters = [
        {
            "type": "text",
            "text": str(customer_name),
        },
        {
            "type": "text",
            "text": str(ticket_number),
        },
        {
            "type": "text",
            "text": str(booking_id_value),
        },
        {
            "type": "text",
            "text": str(visit_date),
        },
        {
            "type": "text",
            "text": str(ride_summary),
        },
        {
            "type": "text",
            "text": str(total_riders),
        },
        {
            "type": "text",
            "text": str(total_amount),
        },
    ]

    # =====================================================
    # PAYLOAD
    # =====================================================

    payload = {
        "phoneNumber": telinfy_phone,

        "template": {
            "name": template_name,

            "language": {
                "code": language_code,
            },

            "components": [

                # =========================================
                # IMAGE HEADER
                # =========================================

                {
                    "type": "header",

                    "parameters": [
                        {
                            "type": "image",

                            "image": {
                                "link": qr_url,
                            },
                        }
                    ],
                },

                # =========================================
                # BODY
                # =========================================

                {
                    "type": "body",
                    "parameters": body_parameters,
                },
            ],
        },
    }

    # =====================================================
    # DEBUG REQUEST
    # =====================================================

    print(
        "\n========================================"
    )
    print(
        "TELINFY WHATSAPP QR REQUEST"
    )
    print(
        "========================================"
    )

    print(
        "URL:",
        url,
    )

    print(
        "TO:",
        telinfy_phone,
    )

    print(
        "TEMPLATE:",
        template_name,
    )

    print(
        "LANGUAGE:",
        language_code,
    )

    print(
        "QR FILE:",
        ticket.qr_image.name,
    )

    print(
        "QR URL:",
        qr_url,
    )

    print(
        "BODY PARAMETER COUNT:",
        len(body_parameters),
    )

    print(
        "BODY PARAMETERS:"
    )

    for index, parameter in enumerate(
        body_parameters,
        start=1,
    ):
        print(
            f"  {{{{{index}}}}}:",
            parameter["text"],
        )

    print(
        "========================================"
    )

    # =====================================================
    # SEND REQUEST
    # =====================================================

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )

        # =================================================
        # DEBUG RESPONSE
        # =================================================

        print(
            "\n========================================"
        )
        print(
            "TELINFY WHATSAPP QR RESULT"
        )
        print(
            "========================================"
        )

        print(
            "HTTP STATUS:",
            response.status_code,
        )

        print(
            "RESPONSE:",
            response.text,
        )

        print(
            "========================================\n"
        )

        # =================================================
        # JSON RESPONSE
        # =================================================

        try:
            response_data = (
                response.json()
            )

        except ValueError:
            response_data = {}

        # =================================================
        # SUCCESS
        # =================================================

        if (
            response.ok
            and response_data.get(
                "success"
            ) is True
        ):

            ticket.whatsapp_sent = True

            ticket.save(
                update_fields=[
                    "whatsapp_sent",
                ]
            )

            data = (
                response_data.get(
                    "data",
                    {}
                )
                or {}
            )

            print(
                "WHATSAPP QR ACCEPTED "
                "BY TELINFY"
            )

            print(
                "RECORD ID:",
                data.get(
                    "recordId"
                ),
            )

            print(
                "QUEUE STATUS:",
                data.get(
                    "queueStatus"
                ),
            )

            print(
                "PHONE:",
                data.get(
                    "phoneNumber"
                ),
            )

            return True

        # =================================================
        # TELINFY FAILED
        # =================================================

        print(
            "WHATSAPP QR SEND FAILED"
        )

        print(
            "STATUS:",
            response.status_code,
        )

        print(
            "RESPONSE:",
            response.text,
        )

        return False

    # =====================================================
    # REQUEST ERROR
    # =====================================================

    except requests.RequestException as error:

        print(
            "\n========================================"
        )
        print(
            "TELINFY WHATSAPP QR "
            "REQUEST ERROR"
        )
        print(
            "========================================"
        )

        print(
            "TYPE:",
            type(error).__name__,
        )

        print(
            "ERROR:",
            repr(error),
        )

        print(
            "========================================\n"
        )

        return False